from app.database.models import async_session
from app.database.models import UserBase
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
