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
        metabolism = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)
    else:
        metabolism = 655.1 + (9.6 * weight) + (1.85 * height) - (4.68 * age)

    if activity == "inactive":
        calorie_intake = metabolism * 1.2
        proteins = weight * 1.5
    elif activity == "light":
        calorie_intake = metabolism * 1.375
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
            else "<b>Описание кнопок:</b>\n\n"
        )
        + "👤 <b>Профиль</b> - ваши данные и КБЖУ\n"
        "📈 <b>Статистика</b> - дневной прогресс\n"
        "🍽️ <b>Питание</b> - подбор рецептов\n"
        "💧 <b>Вода</b> - контроль водного баланса\n"
        "🔒 <b>Конфиденциальность</b> - политика конфиденциальности\n"
        "❓ <b>Помощь</b> - инструкция по использованию\n\n"
        "Выберите раздел:"
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
        f"  ⚖️ Вес: <code>{user_data.weight} кг</code>\n"
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


def build_daily_stats_message(user, meals_sum, water_sum):
    remaining_calories = max(user.calorie_intake - meals_sum["calories"], 0)
    remaining_proteins = max(user.proteins - meals_sum["proteins"], 0)
    remaining_fats = max(user.fats - meals_sum["fats"], 0)
    remaining_carbons = max(user.carbons - meals_sum["carbons"], 0)
    remaining_water = max(user.water - water_sum, 0)

    message_text = (
        "📊 <b>Моё КБЖУ</b>\n\n"
        "🔥 <b>Калории:</b>\n"
        f"  Осталось: <code>{remaining_calories} ккал</code>\n"
        f"  Норма: <code>{user.calorie_intake} ккал</code>\n\n"
        "🍗 <b>Белки:</b>\n"
        f"  Осталось: <code>{remaining_proteins} г</code>\n"
        f"  Норма: <code>{user.proteins} г</code>\n\n"
        "🥑 <b>Жиры:</b>\n"
        f"  Осталось: <code>{remaining_fats} г</code>\n"
        f"  Норма: <code>{user.fats} г</code>\n\n"
        "🍚 <b>Углеводы:</b>\n"
        f"  Осталось: <code>{remaining_carbons} г</code>\n"
        f"  Норма: <code>{user.carbons} г</code>\n\n"
        "💧 <b>Вода:</b>\n"
        f"  Осталось: <code>{remaining_water} мл</code>\n"
        f"  Норма: <code>{user.water} мл</code>"
    )
    return message_text


def build_recipe_message(recipe):
    message_text = (
        f"<b>{recipe.title} ({recipe.calories} ккал)</b>\n\n"
        f"БЖУ: {recipe.proteins} г. белков | {recipe.fats} г. жиров | {recipe.carbons} г. углеводов\n\n"
        "📝 Ингредиенты:\n"
        f"{recipe.ingredients}\n\n"
        f"<blockquote>👩‍🍳 Способ приготовления:\n\n{recipe.instructions}</blockquote>\n\n"
        f"💚 {recipe.comments}"
    )
    return message_text


def build_daily_nutrition_message(meals_list):
    if not meals_list:
        return (
            "🍽️ На сегодня блюда еще не выбраны!\n\n"
            "📝 Используйте меню, чтобы добавить блюда в свой дневной рацион ✨"
        )

    categories = {}
    for meal in meals_list:
        category = meal.category
        if category not in categories:
            categories[category] = []
        categories[category].append(meal)

    message_text = "🍽️ <b>Ваше меню на сегодня:</b>\n\n"

    category_emojis = {"breakfast": "🌅", "lunch": "🍲", "dinner": "🌙"}

    for category, meals in categories.items():
        emoji = category_emojis.get(category.lower(), "🍽️")
        message_text += (
            f"{emoji} <b>{CATEGORIES_MAPPING.get(category, "").capitalize()}:</b>\n"
        )

        for meal in meals:
            message_text += f"{meal.title} ({meal.calories} ккал)\n"

        message_text += "\n"

    message_text += "📖 <i>Для просмотра рецепта выберите блюдо из списка ниже! 👇</i>"

    return message_text


def build_help_message(user_exists):
    message_text = (
        "🆘 <b>Помощь по использованию бота</b>\n\n"
        "📊 <b>Мониторинг питания</b>\n"
        "• <b>Профиль</b> - просмотр и редактирование данных\n"
        "• <b>Моё КБЖУ</b> - дневные показатели\n"
        "• <b>Питание на день</b> - подбор рецептов по категориям:\n"
        "  🥞 Завтрак   🍱 Обед   🧆 Ужин\n\n"
        "💧 <b>Отслеживание воды</b>\n"
        "• Выбирайте стандартные объёмы или вводите свой\n"
        "• Бот рассчитывает вашу дневную норму\n"
        "• Вся статистика сохраняется\n\n"
        "⚙️ <b>Редактирование параметров</b>\n"
        '• В разделе "👤 Профиль" нажмите "✍ Изменить профиль"\n'
        "• Можно изменить любые данные\n"
        "• Норма КБЖУ пересчитается автоматически\n\n"
        "🔍 <b>Поиск рецептов</b>\n"
        "• Рецепты подбираются под вашу норму калорий\n"
        "• Можно просматривать разные варианты\n"
        "• Добавляйте рецепты в дневной рацион\n\n"
        + (
            "👋 <b>Похоже, вы ещё не зарегистрированы!</b>\n"
            "Чтобы использовать все возможности бота, нужно пройти быструю регистрацию.\n"
            "Напишите /start чтобы начать! 🚀\n\n"
            if not user_exists
            else ""
        )
    )
    return message_text


def build_not_registered_message():
    message_text = (
        "👋 <b>Похоже, вы ещё не зарегистрированы!</b>\n\n"
        "Чтобы использовать все возможности бота, нужно пройти быструю регистрацию.\n\n"
        "Напишите /start чтобы начать! 🚀"
    )
    return message_text


async def is_user_in_chat(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except (TelegramForbiddenError, TelegramBadRequest):
        return False
