"""
POST /api/v1/analysis — Create analysis record (admin)
Also exposes a trigger endpoint to run AI analysis on a news item.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.connection import get_db
from database.models import Analysis, News, Users
from schemas.analysis import AnalysisCreate, AnalysisOut
from services.analysis_service import analyze_article
from middlewares.auth_middleware import require_admin

router = APIRouter()


@router.post("/", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    data: AnalysisCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Создать запись анализа вручную (только admin — Ф)."""
    analysis = Analysis(**data.model_dump())
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis


@router.post("/trigger/{news_id}", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def trigger_analysis(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_admin),
):
    """Запустить ИИ-анализ для новости и разослать уведомления заинтересованным пользователям."""
    # Получаем новость (вместе с её категорией)
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    # Вызов ИИ Gemini
    from services.analysis_service import analyze_article
    ai_result = analyze_article(news.title, news.content)

    # Сохраняем анализ
    analysis = Analysis(
        news_id=news_id,
        summary=ai_result["summary"],
        sentiment=ai_result["sentiment"],
        impact=ai_result["impact"],
        confidence=ai_result["confidence"],
    )
    news.sentiment_score = ai_result["sentiment_score"]
    news.impact_score = ai_result["impact_score"]

    db.add(analysis)
    await db.flush() # flush, чтобы получить analysis.id

    # Логика уведомлений — ищем всех пользователей, подписанных на категорию этой новости
    from database.models import UserCategory, Notification
    from services.notification_service import manager
    
    if news.category_id:
        users_query = await db.execute(
            select(UserCategory.user_id).where(UserCategory.category_id == news.category_id)
        )
        user_ids = [row[0] for row in users_query.all()]
        
        # Для каждого создаём уведомление
        for user_id in user_ids:
            notif = Notification(
                user_id=user_id,
                title=f"Новый ИИ Анализ: {ai_result['sentiment'].upper()} сигнал",
                message=f"{news.title}\n\nРезюме: {ai_result['summary']}\nВажность: {ai_result['impact']}",
            )
            db.add(notif)
            await db.flush()
            
            # Отправка по WebSocket (если онлайн)
            await manager.send_to_user(
                user_id,
                {
                    "type": "notification",
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                }
            )

    await db.commit()
    await db.refresh(analysis)
    
    # Также уведомляем всех админов
    admin_query = await db.execute(select(Users.id).where(Users.role == "admin"))
    for admin_id in [row[0] for row in admin_query.all()]:
        await manager.send_to_user(
            admin_id,
            {
                "type": "notification",
                "title": "Система",
                "message": f"Анализ завершен для ID: {news_id}"
            }
        )
            
    return analysis

