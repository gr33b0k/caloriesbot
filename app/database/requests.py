from app.database.models import async_session
from app.database.models import UserBase, WaterLog, Recipe, RecipeLog
from sqlalchemy import select, delete, func, update


async def set_user(data):
    async with async_session() as session:
        user = await session.scalar(
            select(UserBase).where(UserBase.telegram_id == data.get("telegram_id"))
        )

        if not user:
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
            await session.commit()


async def get_user(telegram_id: int) -> UserBase | None:
    async with async_session() as session:
        return await session.scalar(
            select(UserBase).where(UserBase.telegram_id == telegram_id)
        )


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
        user = await session.scalar(
            select(UserBase).where(UserBase.telegram_id == telegram_id)
        )
        if not user:
            return
        user.goal = goal
        user.calorie_intake = calorie_intake
        user.proteins = proteins
        user.fats = fats
        user.carbons = carbons
        await session.commit()


# ----- Recipes API -----


async def seed_recipes_if_empty() -> None:
    async with async_session() as session:
        count = (await session.execute(select(Recipe))).scalars().first()
        if count:
            return
        demo = [
            Recipe(
                title="Овсянка с ягодами",
                category="breakfast",
                calories=350,
                proteins=15,
                fats=8,
                carbons=55,
                weight_grams=300,
                image_url="https://via.placeholder.com/640x360.png?text=Breakfast",
                instructions="Сварите овсянку на воде/молоке, добавьте ягоды и орехи.",
            ),
            Recipe(
                title="Куриная грудка с рисом",
                category="lunch",
                calories=480,
                proteins=40,
                fats=10,
                carbons=60,
                weight_grams=350,
                image_url="https://via.placeholder.com/640x360.png?text=Lunch",
                instructions="Отварите рис, обжарьте куриную грудку, подайте вместе.",
            ),
            Recipe(
                title="Творог с мёдом",
                category="snack",
                calories=220,
                proteins=20,
                fats=5,
                carbons=20,
                weight_grams=200,
                image_url="https://via.placeholder.com/640x360.png?text=Snack",
                instructions="Смешайте творог с мёдом, можно добавить орехи.",
            ),
            Recipe(
                title="Лосось с овощами",
                category="dinner",
                calories=500,
                proteins=35,
                fats=25,
                carbons=25,
                weight_grams=350,
                image_url="https://via.placeholder.com/640x360.png?text=Dinner",
                instructions="Запеките лосося и овощи в духовке 15–20 минут.",
            ),
        ]
        session.add_all(demo)
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
        session.add(RecipeLog(telegram_id=telegram_id, recipe_id=recipe_id))
        await session.commit()


async def list_selected_recipes(telegram_id: int) -> list[RecipeLog]:
    async with async_session() as session:
        result = await session.execute(
            select(RecipeLog).where(RecipeLog.telegram_id == telegram_id)
        )
        return list(result.scalars().all())


async def delete_selected_recipe(entry_id: int, telegram_id: int) -> None:
    async with async_session() as session:
        await session.execute(
            delete(RecipeLog).where(
                (RecipeLog.id == entry_id) & (RecipeLog.telegram_id == telegram_id)
            )
        )
        await session.commit()


# ----- Aggregations for daily stats -----


async def get_today_recipes_sum(telegram_id: int) -> dict:
    async with async_session() as session:
        # Sum by joining logs with recipes
        result = await session.execute(
            select(
                func.coalesce(func.sum(Recipe.calories), 0),
                func.coalesce(func.sum(Recipe.proteins), 0),
                func.coalesce(func.sum(Recipe.fats), 0),
                func.coalesce(func.sum(Recipe.carbons), 0),
            )
            .select_from(RecipeLog)
            .join(Recipe, Recipe.id == RecipeLog.recipe_id)
        )
        cal, p, f, c = result.first()
        return {
            "calories": int(cal),
            "proteins": int(p),
            "fats": int(f),
            "carbons": int(c),
        }


async def get_today_water_sum(telegram_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
                WaterLog.telegram_id == telegram_id
            )
        )
        return int(result.scalar() or 0)
