from app.database.models import async_session
from app.database.models import UserBase, WaterLog, Recipe, DailyMenu
from sqlalchemy import exists, select, delete, func, update
from sqlalchemy.orm import selectinload


async def set_user(data):
    async with async_session() as session:
        if not data.get("user_exists"):
            session.add(
                UserBase(
                    telegram_id=data.get("telegram_id"),
                    name=data.get("name"),
                    age=data.get("age"),
                    sex=data.get("sex"),
                    height=data.get("height"),
                    weight=data.get("weight"),
                    activity=data.get("activity"),
                    goal=data.get("goal"),
                    calorie_intake=data.get("calorie_intake"),
                    proteins=data.get("proteins"),
                    fats=data.get("fats"),
                    carbons=data.get("carbons"),
                    water=data.get("water"),
                )
            )
        else:
            telegram_id = data.get("telegram_id")
            await session.execute(
                update(UserBase)
                .where(UserBase.telegram_id == telegram_id)
                .values(
                    **{
                        key: value
                        for key, value in data.items()
                        if key != "user_exists"
                    }
                )
            )
            await session.execute(
                delete(DailyMenu).where(DailyMenu.telegram_id == telegram_id)
            )
            await session.execute(
                delete(WaterLog).where(WaterLog.telegram_id == telegram_id)
            )
        await session.commit()


async def get_user(telegram_id: int) -> UserBase | None:
    async with async_session() as session:
        return await session.scalar(
            select(UserBase).where(UserBase.telegram_id == telegram_id)
        )


async def user_exists(telegram_id: int) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(exists().where(UserBase.telegram_id == telegram_id))
        )
        return bool(result)


async def update_user_info(telegram_id: int, **kwargs):
    async with async_session() as session:
        if not kwargs:
            return

        await session.execute(
            update(UserBase).where(UserBase.telegram_id == telegram_id).values(**kwargs)
        )
        await session.commit()


async def add_water_log(telegram_id: int, amount_ml: int) -> None:
    async with async_session() as session:
        session.add(WaterLog(telegram_id=telegram_id, amount_ml=amount_ml))
        await session.commit()


async def get_recipes_by_category_and_limit(
    category: str, max_calories: int
) -> list[Recipe]:
    async with async_session() as session:
        result = await session.execute(
            select(Recipe).where(
                Recipe.category == category, Recipe.calories <= max_calories
            )
        )
        return list(result.scalars().all())


async def add_recipe_selection(telegram_id: int, recipe_id: int) -> None:
    async with async_session() as session:
        session.add(DailyMenu(telegram_id=telegram_id, recipe_id=recipe_id))
        await session.commit()


async def get_recipe(recipe_id):
    async with async_session() as session:
        return await session.scalar(select(Recipe).where(Recipe.id == recipe_id))


async def list_selected_recipes(telegram_id: int) -> list[DailyMenu]:
    async with async_session() as session:
        result = await session.execute(
            select(DailyMenu)
            .options(selectinload(DailyMenu.recipe))
            .where(DailyMenu.telegram_id == telegram_id)
        )

        daily_menus = result.scalars().all()
        recipes = [menu.recipe for menu in daily_menus]
        return recipes


async def delete_selected_recipe(entry_id: int, telegram_id: int) -> None:
    async with async_session() as session:
        result_id = await session.scalar(
            select(DailyMenu.id)
            .where(
                (DailyMenu.recipe_id == entry_id)
                & (DailyMenu.telegram_id == telegram_id)
            )
            .limit(1)
        )

        await session.execute(delete(DailyMenu).where((DailyMenu.id == result_id)))
        await session.commit()


async def get_today_recipes_sum(telegram_id: int) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(
                func.coalesce(func.sum(Recipe.calories), 0),
                func.coalesce(func.sum(Recipe.proteins), 0),
                func.coalesce(func.sum(Recipe.fats), 0),
                func.coalesce(func.sum(Recipe.carbons), 0),
            )
            .select_from(DailyMenu)
            .where(DailyMenu.telegram_id == telegram_id)
            .join(Recipe, Recipe.id == DailyMenu.recipe_id)
        )
        calories, proteins, fats, carbons = result.first()
        return {
            "calories": int(calories),
            "proteins": int(proteins),
            "fats": int(fats),
            "carbons": int(carbons),
        }


async def get_today_water_sum(telegram_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
                WaterLog.telegram_id == telegram_id
            )
        )
        return int(result.scalar() or 0)
