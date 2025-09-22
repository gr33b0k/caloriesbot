from sqlalchemy import BigInteger, String, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

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


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
