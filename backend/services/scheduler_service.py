"""
Insight IS — APScheduler Service
Runs background tasks like fetching news every 30 seconds.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy.future import select

from database.connection import async_session_maker
from database.models import News, Analysis, UserCategory, Notification, Users, Category
from services.news_service import news_service
from services.analysis_service import analyze_article
from services.notification_service import manager

scheduler = AsyncIOScheduler()

async def fetch_and_analyze_news_job():
    logger.info("Starting scheduled job: fetch_and_analyze_news_job")
    try:
        # 1. Fetch news
        articles = await news_service.fetch_all(query="finance")
        if not articles:
            logger.info("No news fetched this time.")
            return

        async with async_session_maker() as db:
            for article_data in articles:
                # 2. Check if news already exists by URL
                url = article_data.get("url")
                if not url:
                    continue
                    
                existing_news = await db.execute(select(News).where(News.url == url))
                if existing_news.scalars().first():
                    continue  # Skip already processed news
                
                # Fetch a default category to attach so notifications work.
                # In production, we would map specific keywords to categories.
                cat_result = await db.execute(select(Category).where(Category.name.in_(["Финансы", "Технологии", "Крипто", "Энергетика"])))
                category = cat_result.scalars().first()
                category_id = category.id if category else None
                
                news = News(
                    title=article_data["title"],
                    content=article_data.get("content", ""),
                    source=article_data.get("source", ""),
                    url=url,
                    publication_date=article_data.get("publication_date"),
                    category_id=category_id
                )
                db.add(news)
                await db.flush() # get news.id
                
                logger.info(f"Analyzing new article: {news.title}")
                try:
                    ai_result = analyze_article(news.title, news.content)
                    
                    analysis = Analysis(
                        news_id=news.id,
                        summary=ai_result["summary"],
                        sentiment=ai_result["sentiment"],
                        impact=ai_result["impact"],
                        confidence=ai_result["confidence"],
                    )
                    news.sentiment_score = ai_result["sentiment_score"]
                    news.impact_score = ai_result["impact_score"]
                    db.add(analysis)
                    await db.flush()

                    # Send notifications to users subscribed to this category
                    if news.category_id:
                        users_query = await db.execute(
                            select(UserCategory.user_id).where(UserCategory.category_id == news.category_id)
                        )
                        user_ids = [row[0] for row in users_query.all()]
                        
                        for user_id in user_ids:
                            notif = Notification(
                                user_id=user_id,
                                title=f"Новый ИИ Анализ: {ai_result['sentiment'].upper()} сигнал",
                                message=f"{news.title}\n\nРезюме: {ai_result['summary']}\nВажность: {ai_result['impact']}",
                            )
                            db.add(notif)
                            await db.flush()
                            
                            await manager.send_to_user(
                                user_id,
                                {
                                    "type": "notification",
                                    "id": notif.id,
                                    "title": notif.title,
                                    "message": notif.message,
                                }
                            )

                    # Always notify admins so they see the activity
                    admin_query = await db.execute(select(Users.id).where(Users.role == "admin"))
                    for admin_id in [row[0] for row in admin_query.all()]:
                        await manager.send_to_user(
                            admin_id,
                            {
                                "type": "notification",
                                "title": "Анализ завершен",
                                "message": f"{news.title} -> {ai_result['sentiment'].upper()}"
                            }
                        )

                except Exception as e:
                    logger.error(f"Error analyzing article {news.id}: {e}")
                    
            await db.commit()
            logger.info("Finished scheduled job: fetch_and_analyze_news_job")

    except Exception as e:
        logger.error(f"Error in fetch_and_analyze_news_job: {e}")

# Run every 30 seconds
scheduler.add_job(fetch_and_analyze_news_job, "interval", seconds=30, id="fetch_news_30s")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
