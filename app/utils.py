from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


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


def build_confirmation_message(data):
    message_text = (
        f"📋 Подтвердите корректность введенной информации: 📋\n\n"
        f"🏷️ <b>Имя:</b> <code>{data['name']}</code>\n"
        f"🎂 <b>Возраст:</b> <code>{data['age']}</code>\n"
        f"📏 <b>Рост:</b> <code>{data['height']} см</code>\n"
        f"⚖️ <b>Вес:</b> <code>{data['weight']} кг</code>\n"
        f"🏃 <b>Уровень активности:</b> <code>{match_activity(data['activity'])}</code>\n"
        f"🎯 <b>Цель:</b> <code>{match_goal(data['goal'])}</code>\n\n"
        "✅ Все данные верны?"
    )
    return message_text


def build_menu_message(is_registration):
    message_text = (
        "🎉 <b>Регистрация завершена!</b> 🎉\n\n"
        if is_registration
        else ""
        "Теперь вы можете использовать все функции бота:\n\n"
        "📊 <b>Основные команды:</b>\n"
        "• /recipes - Получить рецепты по категориям\n"
        "• /delete_meals - Удалить добавленные приемы пищи\n"
        "• /show_today_calories - Показать остаток КБЖУ на сегодня\n"
        "• /track_water - Отметить потребление воды\n"
        "• /my_goal - Посмотреть/изменить цель\n\n"
        "❓ <b>Помощь:</b>\n"
        "• /help - Список всех команд\n"
        "• /privacy - Политика конфиденциальности\n\n"
        "💡 <b>Совет:</b> Начните с команды /recipes чтобы выбрать блюда на день!"
    )
    return message_text


def build_profile_message(user_data):
    message_text = (
        "👤 <b>Мой профиль</b>\n\n"
        "📝 <b>Личная информация:</b>\n"
        f"   🏷️ Имя: <code>{user_data.name}</code>\n"
        f"   🎂 Возраст: <code>{user_data.age} лет</code>\n"
        f"   📏 Рост: <code>{user_data.height} см</code>\n"
        f"   ⚖️ Вес: <code>{user_data.weight} кг</code>\n\n"
        "🎯 <b>Настройки:</b>\n"
        f"   🏃 Активность: <code>{match_activity(user_data.activity)}</code>\n"
        f"   🎯 Цель: <code>{match_goal(user_data.goal)}</code>\n\n"
        "📊 <b>Дневные нормы:</b>\n"
        f"   🔥 Калории: <code>{user_data.calorie_intake} ккал</code>\n"
        f"   🍗 Белки: <code>{user_data.proteins} г</code>\n"
        f"   🥑 Жиры: <code>{user_data.fats} г</code>\n"
        f"   🍚 Углеводы: <code>{user_data.carbons} г</code>\n"
        f"   💧 Вода: <code>{user_data.water} мл</code>\n\n"
        "✏️ <i>Хотите что-то изменить? Выберите поле для редактирования:</i>"
    )
    return message_text


def match_activity(activity):
    mapping = {
        "inactive": "сидячий образ жизни",
        "light": "легкая активность",
        "moderate": "умеренная активность",
        "high": "активный образ жизни",
        "very-high": "очень активный образ жизни",
    }
    return mapping.get(activity, activity)


def match_goal(goal):
    mapping = {
        "loss": "похудение",
        "maintain": "поддержание веса",
        "gain": "набор мышечной массы",
    }
    return mapping.get(goal, goal)


async def is_user_in_chat(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except (TelegramForbiddenError, TelegramBadRequest):
        return False
