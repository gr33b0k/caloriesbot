from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from app.constants import *


def calculate_calories(data: dict) -> dict:
    age = int(data["age"])
    sex = data["sex"]
    height = int(data["height"])
    weight = int(data["weight"])
    activity = data["activity"]
    goal = data["goal"]

    if sex == "male":
        metabolism = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        metabolism = 10 * weight + 6.25 * height - 5 * age - 161

    if activity == "inactive":
        calorie_intake = metabolism * 1.2
        proteins = weight * 1.5
    elif activity == "light":
        calorie_intake = metabolism * 1.38
        proteins = weight * 1.5
    elif activity == "moderate":
        calorie_intake = metabolism * 1.55
        proteins = weight * 2
    elif activity == "high":
        calorie_intake = metabolism * 1.73
        proteins = weight * 2.5
    elif activity == "very-high":
        calorie_intake = metabolism * 2.2
        proteins = weight * 3

    if goal == "loss":
        calorie_intake -= (calorie_intake * 15) / 100
    elif goal == "gain":
        calorie_intake += (calorie_intake * 15) / 100

    fats = weight * 1.3
    carbons = (calorie_intake - proteins * 4.1 - fats * 9.3) / 4.1

    water = weight * 30

    return {
        "calorie_intake": int(calorie_intake),
        "proteins": int(proteins),
        "fats": int(fats),
        "carbons": int(carbons),
        "water": int(water),
    }


def build_menu_message(is_registration):
    message_text = (
        (
            "🎉 <b>Регистрация завершена!</b> 🎉\n\nТеперь вы можете использовать все функции бота:\n\n"
            if is_registration
            else ""
        )
        + "📊 <b>Основные команды:</b>\n"
        "• /recipes - Получить рецепты по категориям\n"
        "• /delete_meals - Удалить добавленные приемы пищи\n"
        "• /show_today_calories - Показать остаток КБЖУ на сегодня\n"
        "• /track_water - Отметить потребление воды\n"
        "• /my_goal - Посмотреть/изменить цель\n\n"
        "❓ <b>Помощь:</b>\n"
        "• /help - Список всех команд\n"
        "• /privacy - Политика конфиденциальности\n\n"
    )
    return message_text


def build_profile_message(user_data):
    message_text = (
        "👤 <b>Мой профиль</b>\n\n"
        "📝 <b>Личная информация:</b>\n"
        f"  🏷️ Имя: <code>{user_data.name}</code>\n"
        f"  🚻 Пол : <code>{SEX_MAPPING.get(user_data.sex, user_data.sex)}</code>\n"
        f"  🎂 Возраст: <code>{user_data.age} лет</code>\n"
        f"  📏 Рост: <code>{user_data.height} см</code>\n"
        f"  ⚖️ Вес: <code>{user_data.weight} кг</code>\n\n"
        f"  🏃 Активность: <code>{ACTIVITY_MAPPING.get(user_data.activity, user_data.activity)}</code>\n"
        f"  🎯 Цель: <code>{GOAL_MAPPING.get(user_data.goal, user_data.goal)}</code>\n"
        "📊 <b>Дневные нормы:</b>\n"
        f"  🔥 Калории: <code>{user_data.calorie_intake} ккал</code>\n"
        f"  🍗 Белки: <code>{user_data.proteins} г</code>\n"
        f"  🥑 Жиры: <code>{user_data.fats} г</code>\n"
        f"  🍚 Углеводы: <code>{user_data.carbons} г</code>\n"
        f"  💧 Вода: <code>{user_data.water} мл</code>\n\n"
        "✏️ <i>Хотите что-то изменить?</i>"
    )
    return message_text


async def is_user_in_chat(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except (TelegramForbiddenError, TelegramBadRequest):
        return False
