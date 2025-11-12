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
            BotCommand(command="start", description="✍ Регистрация"),
            BotCommand(command="menu", description="⚙️ Меню"),
            BotCommand(command="help", description="❓ Помощь"),
            BotCommand(command="privacy", description="🔒 Политика конфиденциальности"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
