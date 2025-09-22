from app.database.models import async_session
from app.database.models import UserBase, WaterLog
from sqlalchemy import select


async def set_user(data):
    async with async_session() as session:
        user = await session.scalar(
            select(UserBase).where(UserBase.telegram_id == data.get("telegram_id"))
        )

        if not user:
            session.add(
                UserBase(
                    telegram_id=data.get("telegram_id"),
                    age=data.get("age"),
                    sex=data.get("sex"),
                    height=data.get("height"),
                    weight=data.get("weight"),
                    activity=data.get("activity"),
                    calorie_intake=data.get("calorie_intake"),
                    proteins=data.get("proteins"),
                    fats=data.get("fats"),
                    carbons=data.get("carbons"),
                    water=data.get("water"),
                )
            )
            await session.commit()


async def get_user(telegram_id: int) -> UserBase | None:
    async with async_session() as session:
        return await session.scalar(
            select(UserBase).where(UserBase.telegram_id == telegram_id)
        )


async def add_water_log(telegram_id: int, amount_ml: int) -> None:
    async with async_session() as session:
        session.add(WaterLog(telegram_id=telegram_id, amount_ml=amount_ml))
        await session.commit()


async def update_user_goal(
    telegram_id: int,
    *,
    goal: str,
    calorie_intake: int,
    proteins: int,
    fats: int,
    carbons: int,
) -> None:
    async with async_session() as session:
        user = await session.scalar(select(UserBase).where(UserBase.telegram_id == telegram_id))
        if not user:
            return
        user.activity = user.activity
        user.sex = user.sex
        user.calorie_intake = calorie_intake
        user.proteins = proteins
        user.fats = fats
        user.carbons = carbons
        await session.commit()