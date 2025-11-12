from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    name: Mapped[str] = mapped_column(String(20))
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
    category: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    calories: Mapped[int] = mapped_column(Integer)
    proteins: Mapped[float] = mapped_column(Float)
    fats: Mapped[float] = mapped_column(Float)
    carbons: Mapped[float] = mapped_column(Float)
    ingredients: Mapped[str] = mapped_column(String(4000))
    instructions: Mapped[str] = mapped_column(String(4000))
    comments: Mapped[str] = mapped_column(String(4000))
    # image_url: Mapped[str] = mapped_column(String(500))


class DailyMenu(Base):
    __tablename__ = "daily_menus"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    recipe: Mapped["Recipe"] = relationship("Recipe")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        info = await conn.execute(text("PRAGMA table_info(water_logs)"))
        cols = [row[1] for row in info]
        if "created_at" not in cols:
            await conn.execute(
                text("ALTER TABLE water_logs ADD COLUMN created_at DATETIME")
            )
