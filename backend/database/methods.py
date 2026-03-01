from aiogram.types import Message
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from settings.settings import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import User

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

Base = declarative_base()
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """
    Инициализирует базу данных, создавая все таблицы, указанные в моделях.

    Осуществляет подключение к базе данных через асинхронный движок SQLAlchemy и создает таблицы,
    определенные в объекте `Base`, если они отсутствуют.

    Примечание:
        `Base.metadata.create_all` используется для создания таблиц, если их еще нет.
        Должна быть вызвана при запуске приложения для первичной инициализации структуры БД.

    Args:
        None

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_user(message: Message):
    """
    Создает нового пользователя в базе данных, если он еще не существует.

    Выполняет поиск по `telegram_id` пользователя. Если пользователь не найден, добавляет
    нового пользователя с указанными `telegram_id`, `username` и `first_name` в базу данных.

    Args:
        message (Message): Объект сообщения от aiogram, содержащий информацию о пользователе,
                           такую как `from_user.id`, `from_user.username`, `from_user.first_name`.

    Returns:
        True если пользователь добавлен в базу данных, иначе False - если пользователь уже существует.

    Примечание:
        - `telegram_id` используется для идентификации пользователя в базе данных.
        - `username` и `first_name` сохраняются как дополнительные поля для удобства.

    Исключения:
        Может возникнуть ошибка при попытке сохранить данные в базу данных, если соединение
        потеряно или есть проблемы с синтаксисом SQL-запроса.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalars().first()
        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(new_user)
            await session.commit()
            return True
        return False