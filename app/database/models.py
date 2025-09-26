from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import text
from datetime import datetime

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(7))
    height: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(30))
    goal: Mapped[str] = mapped_column(String(30))
    calorie_intake: Mapped[int] = mapped_column(Integer)
    proteins: Mapped[int] = mapped_column(Integer)
    fats: Mapped[int] = mapped_column(Integer)
    carbons: Mapped[int] = mapped_column(Integer)
    water: Mapped[int] = mapped_column(Integer)


class WaterLog(Base):
    __tablename__ = "water_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)
    amount_ml: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(30))  # breakfast/lunch/snack/dinner
    calories: Mapped[int] = mapped_column(Integer)  # per portion
    proteins: Mapped[int] = mapped_column(Integer)
    fats: Mapped[int] = mapped_column(Integer)
    carbons: Mapped[int] = mapped_column(Integer)
    weight_grams: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(500))
    instructions: Mapped[str] = mapped_column(String(4000))


class RecipeLog(Base):
    __tablename__ = "recipe_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # lightweight migration: add created_at to water_logs if missing
        info = await conn.execute(text("PRAGMA table_info(water_logs)"))
        cols = [row[1] for row in info]
        if "created_at" not in cols:
            await conn.execute(
                text("ALTER TABLE water_logs ADD COLUMN created_at DATETIME")
            )
        # add goal to users if missing
        info_users = await conn.execute(text("PRAGMA table_info(users)"))
        user_cols = [row[1] for row in info_users]
        if "goal" not in user_cols:
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN goal VARCHAR(30)")
            )
            # set default goal for existing rows
            await conn.execute(
                text("UPDATE users SET goal = 'maintain' WHERE goal IS NULL")
            )
