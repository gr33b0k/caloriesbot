import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from app.handlers import router
from app.database.models import async_main

load_dotenv()


async def main():
    await async_main()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.set_my_commands(
        [
            BotCommand(command="recipes", description="Выбрать рецепт 😜"),
            # BotCommand(command="add_meal", description="Добавить еду 🍽"),
            BotCommand(command="delete_meals", description="Удалить приём пищи 🗑"),
            BotCommand(command="show_today_calories", description="Моё КБЖУ ✅"),
            # BotCommand(command="recommend_food", description="Посоветуй что поесть 🍽"),
            # BotCommand(command="plan", description="Планирование питания 📅"),
            BotCommand(command="track_water", description="Выпить воды 💧"),
            BotCommand(command="my_goal", description="Моя цель 🎉"),
            # BotCommand(command="change_products", description="Замена продуктов 🔄"),
            BotCommand(command="help", description="Помощь 🛠"),
            BotCommand(command="privacy", description="Политика конфиденциальности"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
