import app.keyboards as kb
import app.database.requests as rq
from app.utils import (
    build_menu_message,
    build_profile_message,
    calculate_calories,
)
from app.constants import *
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()


# region States


class RegistrationStates(StatesGroup):
    waiting_name = State()
    waiting_age = State()
    waiting_sex = State()
    waiting_height = State()
    waiting_weight = State()
    waiting_activity = State()
    waiting_goal = State()
    waiting_loss_bucket = State()
    waiting_loss_rate = State()
    completed = State()


class WaterStates(StatesGroup):
    waiting_custom_value = State()


class EditProfileStates(StatesGroup):
    waiting_value = State()


# endregion


# region General commands


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.reply(
        "Давайте познакомимся! 🙂 Пожалуйста, напишите своё имя.",
    )
    await state.update_data(telegram_id=message.from_user.id)
    await state.set_state(RegistrationStates.waiting_name)


# @router.message(Command("recommend_food"))
# async def handleRecommendFood(message: Message):
#     await message.answer(
#         "Посоветуй что поесть 🍽\nНапишите время приёма пищи (завтрак/обед/ужин) — я подскажу идеи."
#     )


# @router.message(Command("plan"))
# async def handlePlan(message: Message):
#     await message.answer(
#         'Планирование питания 📅\nОпишите период (например: "на неделю") и предпочтения.'
#     )


# @router.message(Command("add_meal"))
# async def handleAddMeal(message: Message):
#     await message.answer(
#         'Добавить еду 🍽\nНапишите, что вы съели и сколько (например: "овсянка 60 г").'
#     )


@router.message(Command("show_today_calories"))
async def show_today_calories_command(message: Message):
    user = await rq.get_user(message.from_user.id)
    if not user:
        await message.answer(
            "Я не нашёл ваших данных. Пройдите регистрацию командой /start."
        )
        return
    meals_sum = await rq.get_today_recipes_sum(message.from_user.id)
    water_sum = await rq.get_today_water_sum(message.from_user.id)
    remaining_cal = max(user.calorie_intake - meals_sum["calories"], 0)
    remaining_p = max(user.proteins - meals_sum["proteins"], 0)
    remaining_f = max(user.fats - meals_sum["fats"], 0)
    remaining_c = max(user.carbons - meals_sum["carbons"], 0)
    remaining_water = max(user.water - water_sum, 0)
    text_lines = []
    text_lines.append("Моё КБЖУ ✅")
    text_lines.append(
        f"🔥 Осталось калорий: {remaining_cal} ккал (из {user.calorie_intake})"
    )
    text_lines.append(f"🍗 Осталось белков: {remaining_p} г (из {user.proteins})")
    text_lines.append(f"🥑 Осталось жиров: {remaining_f} г (из {user.fats})")
    text_lines.append(f"🍚 Осталось углеводов: {remaining_c} г (из {user.carbons})")
    text_lines.append(f"💧 Осталось воды: {remaining_water} мл (норма {user.water})")
    await message.answer("\n".join(text_lines))


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Помощь 🛠\nДоступные команды:\n"
        "/recipes, /delete_meals, /show_today_calories,\n"
        "/track_water, /my_goal, /help, /privacy"
    )


@router.message(Command("privacy"))
async def privacy_command(message: Message):
    await message.answer(
        "Политика конфиденциальности\nМы храним только данные, которые вы нам отправляете, для расчётов КБЖУ."
    )


# @router.message(Command("change_products"))
# async def handleChangeProducts(message: Message):
#     await message.answer(
#         'Замена продуктов 🔄\nНапишите продукт и альтернативу (например: "майонез → греческий йогурт").'
#     )


# endregion


# region Recipes


@router.message(Command("recipes"))
async def recipes_command(message: Message):
    await rq.seed_recipes_if_empty()
    await message.answer(
        "Выберите приём пищи:", reply_markup=kb.recipes_categories_keyboard
    )


@router.message(Command("delete_meals"))
async def delete_meals_command(message: Message):
    entries = await rq.list_selected_recipes(message.from_user.id)
    if not entries:
        await message.answer("У вас нет добавленных рецептов")
        return
    await message.answer(
        "Удалить приём пищи 🗑\nВыберите запись для удаления:",
        reply_markup=kb.build_delete_recipe_keyboard(entries),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("recipes:"))
async def recipes_by_category(query: CallbackQuery):
    await query.answer()
    _, category = query.data.split(":")
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.answer("Сначала пройдите регистрацию: /start")
        return
    max_cal = user.calorie_intake
    recipes = await rq.get_recipes_by_category_and_limit(category, max_cal)
    if not recipes:
        await query.message.answer("Подходящих рецептов не найдено")
        return
    await query.message.edit_text(
        "😋 Выберите рецепт:", reply_markup=kb.build_recipes_keyboard(recipes)
    )


@router.callback_query(
    lambda c: c.data
    and c.data.startswith("pick_recipe:")
    and not c.data.endswith("back")
)
async def pick_recipe(query: CallbackQuery):
    await query.answer()
    _, recipe_id = query.data.split(":")
    await rq.add_recipe_selection(query.from_user.id, int(recipe_id))
    await query.message.edit_text(
        "Вы успешно добавили рецепт!\n\nВыберите приём пищи:",
        reply_markup=kb.recipes_categories_keyboard,
    )


@router.callback_query(
    lambda c: c.data and c.data.startswith("pick_recipe:") and c.data.endswith("back")
)
async def back_to_categories(query: CallbackQuery):
    await query.message.edit_text(
        "Выберите приём пищи:", reply_markup=kb.recipes_categories_keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("del_recipe:"))
async def delete_recipe_entry(query: CallbackQuery):
    await query.answer()
    _, entry_id = query.data.split(":")
    await rq.delete_selected_recipe(int(entry_id), query.from_user.id)
    entries = await rq.list_selected_recipes(query.from_user.id)
    await query.message.edit_text(
        "Удалить приём пищи 🗑\nВыберите запись для удаления:",
        reply_markup=kb.build_delete_recipe_keyboard(entries),
    )


# endregion


# region Water


@router.message(Command("track_water"))
async def track_water_command(message: Message):
    user = await rq.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"Выпить воды 💧\nВаша дневная норма: {user.water} мл.",
            reply_markup=kb.track_water_keyboard,
        )
    else:
        await message.answer(
            "Выпить воды 💧\nЧтобы рассчитать норму, сначала пройдите регистрацию командой /start."
        )


@router.callback_query(lambda c: c.data and c.data.startswith("water:"))
async def water_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, value = query.data.split(":")
    if value == "custom":
        await query.message.answer("Введите объём воды в мл (целое число):")
        await state.set_state(WaterStates.waiting_custom_value)
        return
    amount_ml = int(value)
    await rq.add_water_log(query.from_user.id, amount_ml)
    await query.message.answer("Вы успешно отметили приём воды")


@router.message(WaterStates.waiting_custom_value)
async def water_custom_value(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer(
            "Пожалуйста, введите целое число в миллилитрах, например 300"
        )
        return
    amount_ml = int(text)
    await rq.add_water_log(message.from_user.id, amount_ml)
    await message.answer("Вы успешно отметили приём воды")
    await state.clear()


# endregion


# region Registration


@router.message(RegistrationStates.waiting_name)
async def name_callback(message: Message, state: FSMContext):
    name_str = message.text.strip()
    if not name_str.isalpha() or len(name_str) < 2 or len(name_str) > 30:
        await message.answer(
            "Пожалуйста, введите корректное имя (только буквы, 2-30 символов)"
        )
        return
    await state.update_data(name=name_str)
    await message.answer("Супер! 🎉 Теперь укажите Ваш возраст")
    await state.set_state(RegistrationStates.waiting_age)


@router.message(RegistrationStates.waiting_age)
async def age_callback(message: Message, state: FSMContext):
    age_str = message.text.strip()
    try:
        age_int = int(age_str)
    except ValueError:
        await message.answer("Пожалуйста, отправьте число в диапазоне 16-100")
        return
    if not (16 <= age_int <= 100):
        await message.answer("Пожалуйста, отправьте число в диапазоне 16-100")
        return
    await state.update_data(age=age_int)
    await message.answer("Отлично! 🙌 Введите ваш рост в сантиметрах")
    await state.set_state(RegistrationStates.waiting_height)


@router.message(RegistrationStates.waiting_height)
async def height_callback(message: Message, state: FSMContext):
    height_str = message.text
    try:
        height_int = int(height_str)
    except ValueError:
        await message.answer("Пожалуйста, отправьте число в диапазоне 120–230")
        return
    if not (120 <= height_int <= 230):
        await message.answer("Пожалуйста, отправь число в диапазоне 120–230")
        return
    await state.update_data(height=height_int)
    await message.answer("А теперь введите ваш вес в килограммах")
    await state.set_state(RegistrationStates.waiting_weight)


@router.message(RegistrationStates.waiting_weight)
async def msg_weight(message: Message, state: FSMContext):
    weight_str = message.text.strip().replace(",", ".")
    try:
        weight_int = int(weight_str)
    except ValueError:
        await message.answer("Пожалуйста, отправь число в диапазоне 35–250")
        return
    if not (35 <= weight_int <= 250):
        await message.answer("Пожалуйста, отправь число в диапазоне 35–250")
        return
    await state.update_data(weight=weight_int)
    await message.answer(
        "Спасибо! 📝 Теперь выберите ваш пол:", reply_markup=kb.sex_keyboard
    )
    await state.set_state(RegistrationStates.waiting_sex)


@router.callback_query(
    RegistrationStates.waiting_sex, lambda c: c.data and c.data.startswith("sex:")
)
async def sex_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, sex = query.data.split(":")
    await state.update_data(sex=sex)
    await query.message.edit_text(
        "Хорошо! 💪 Теперь выберите ваш уровень активности. Это поможет точнее рассчитать норму калорий",
        reply_markup=kb.activity_keyboard,
    )
    await state.set_state(RegistrationStates.waiting_activity)


@router.callback_query(
    RegistrationStates.waiting_activity,
    lambda c: c.data and c.data.startswith("activity:"),
)
async def cb_activity(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, activity = query.data.split(":")
    await state.update_data(activity=activity)
    await query.message.edit_text(
        "Почти готово! 🌟 Укажите вашу цель: поддерживать вес, похудеть или набрать массу",
        reply_markup=kb.goal_keyboard,
    )
    await state.set_state(RegistrationStates.waiting_goal)


@router.callback_query(
    RegistrationStates.waiting_goal, lambda c: c.data and c.data.startswith("goal:")
)
async def goal_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, goal = query.data.split(":")
    await state.update_data(goal=goal)
    data = await state.get_data()
    results = calculate_calories(data)
    combined_data = {**data, **results}
    await rq.set_user(combined_data)
    message_text = build_menu_message(True)
    await query.message.edit_text(
        message_text, parse_mode="HTML", reply_markup=kb.menu_keyboard
    )
    await state.clear()


# endregion


# region Menu


@router.message(Command("menu"))
async def menu_command(message: Message):
    user = await rq.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return
    await message.answer(
        build_menu_message(False), reply_markup=kb.menu_keyboard, parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    await query.answer()
    message_text = build_menu_message(False)
    await query.message.edit_text(
        message_text, parse_mode="HTML", reply_markup=kb.menu_keyboard
    )


@router.callback_query(lambda c: c.data and c.data == "menu:profile")
async def menu_profile(query: CallbackQuery):
    await query.answer()
    user_id = query.from_user.id
    user_data = await rq.get_user(user_id)
    message_text = build_profile_message(user_data)
    await query.message.edit_text(
        message_text, parse_mode="HTML", reply_markup=kb.profile_keyboard
    )


@router.callback_query(lambda c: c.data and c.data == "menu:daily_stats")
async def menu_daily_stats(query: CallbackQuery):
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(
            "Я не нашёл ваших данных. Пройдите регистрацию командой /start."
        )
        return
    meals_sum = await rq.get_today_recipes_sum(query.from_user.id)
    water_sum = await rq.get_today_water_sum(query.from_user.id)
    remaining_calories = max(user.calorie_intake - meals_sum["calories"], 0)
    remaining_proteins = max(user.proteins - meals_sum["proteins"], 0)
    remaining_fats = max(user.fats - meals_sum["fats"], 0)
    remaining_carbons = max(user.carbons - meals_sum["carbons"], 0)
    remaining_water = max(user.water - water_sum, 0)
    text_lines = []
    text_lines.append("Моё КБЖУ ✅")
    text_lines.append(
        f"🔥 Осталось калорий: {remaining_calories} ккал (из {user.calorie_intake})"
    )
    text_lines.append(
        f"🍗 Осталось белков: {remaining_proteins} г (из {user.proteins})"
    )
    text_lines.append(f"🥑 Осталось жиров: {remaining_fats} г (из {user.fats})")
    text_lines.append(
        f"🍚 Осталось углеводов: {remaining_carbons} г (из {user.carbons})"
    )
    text_lines.append(f"💧 Осталось воды: {remaining_water} мл (норма {user.water})")
    await query.message.edit_text(
        "\n".join(text_lines), reply_markup=kb.back_to_menu_keyboard
    )


# endregion


# region Profile


@router.callback_query(lambda c: c.data == "profile:edit")
async def edit_profile(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        "Выберите, что Вы хотите поменять:", reply_markup=kb.edit_profile_keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("edit:"))
async def edit_field_selection(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, field = query.data.split(":")

    await state.update_data(editing_field=field)

    messages = {
        "name": "🏷️ Введите Ваше имя:",
        "sex": "🚻 Выберите Ваш пол:",
        "age": "🎂 Введите Ваш возраст:",
        "height": "📏 Введите Ваш рост:",
        "weight": "⚖️ Введите Ваш вес:",
        "activity": "🏃 Выберите новый уровень активности:",
        "goal": "🎯 Выберите новую цель:",
    }

    if field in ["sex", "activity", "goal"]:
        keyboards = {
            "activity": kb.activity_keyboard,
            "sex": kb.sex_keyboard,
            "goal": kb.goal_keyboard,
        }
        await query.message.edit_text(messages[field], reply_markup=keyboards[field])
    else:
        await query.message.edit_text(messages[field])

    await state.set_state(EditProfileStates.waiting_value)


@router.message(EditProfileStates.waiting_value)
async def process_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["editing_field"]

    if field in ["sex", "activity", "goal"]:
        return

    value = message.text.strip()

    validation_rules = {
        "name": {
            "check": lambda v: v.isalpha() and 2 <= len(v) <= 30,
            "error": "Пожалуйста, введите корректное имя (только буквы, 2-30 символов)",
        },
        "age": {
            "check": lambda v: v.isdigit() and 16 <= int(v) <= 100,
            "error": "Пожалуйста, введите число в диапазоне 16-100",
        },
        "height": {
            "check": lambda v: v.isdigit() and 120 <= int(v) <= 230,
            "error": "Пожалуйста, введите число в диапазоне 120-230",
        },
        "weight": {
            "check": lambda v: v.replace(",", "").replace(".", "").isdigit()
            and 35 <= float(v.replace(",", ".")) <= 250,
            "error": "Пожалуйста, введите число в диапазоне 35-250",
        },
    }

    if field in validation_rules:
        rule = validation_rules[field]
        if not rule["check"](value):
            await message.answer(rule["error"])
            return

        if field in ["age", "height"]:
            value = int(value)
        elif field == "weight":
            value = int(float(value.replace(",", ".")))

    user = await rq.get_user(message.from_user.id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        await state.clear()
        return

    if field == "name":
        await rq.update_user_info(message.from_user.id, **{field: value})

    if field in ["weight", "height", "age"]:
        user_data = {
            "age": user.age if field != "age" else value,
            "sex": user.sex,
            "height": user.height if field != "height" else value,
            "weight": user.weight if field != "weight" else value,
            "activity": user.activity,
            "goal": user.goal,
        }
        results = calculate_calories(user_data)
        await rq.update_user_info(message.from_user.id, **results)

    updated_user = await rq.get_user(message.from_user.id)
    success_message = f"✅ {FIELDS_MAPPING.get(field, field).capitalize()} успешно {"обновлен" if field != "name" else "обновлено"}!\n\n"
    profile_message = build_profile_message(updated_user)

    await message.answer(
        success_message + profile_message,
        parse_mode="HTML",
        reply_markup=kb.profile_keyboard,
    )
    await state.clear()


async def _process_callback_edit(query: CallbackQuery, state: FSMContext, field):
    await query.answer()
    data = await state.get_data()

    if data.get("editing_field") != field:
        return

    _, value = query.data.split(":")

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.answer("Ошибка: пользователь не найден")
        await state.clear()
        return

    user_data = {
        "age": user.age,
        "sex": value if field == "sex" else user.sex,
        "height": user.height,
        "weight": user.weight,
        "activity": value if field == "activity" else user.activity,
        "goal": value if field == "goal" else user.goal,
    }
    results = calculate_calories(user_data)
    new_data = {**{field: value}, **results}
    await rq.update_user_info(query.from_user.id, **new_data)

    updated_user = await rq.get_user(query.from_user.id)
    success_message = f"✅ {FIELDS_MAPPING.get(field, field).capitalize()} успешно {'обновлен' if field != 'goal' else 'обновлена'}!\n\n"
    profile_message = build_profile_message(updated_user)

    await query.message.edit_text(
        success_message + profile_message,
        parse_mode="HTML",
        reply_markup=kb.profile_keyboard,
    )
    await state.clear()


@router.callback_query(
    EditProfileStates.waiting_value, lambda c: c.data and c.data.startswith("sex:")
)
async def edit_sex_callback(query: CallbackQuery, state: FSMContext):
    await _process_callback_edit(query, state, "sex")


@router.callback_query(
    EditProfileStates.waiting_value, lambda c: c.data and c.data.startswith("activity:")
)
async def edit_activity_callback(query: CallbackQuery, state: FSMContext):
    await _process_callback_edit(query, state, "activity")


@router.callback_query(
    EditProfileStates.waiting_value, lambda c: c.data and c.data.startswith("goal:")
)
async def edit_goal_callback(query: CallbackQuery, state: FSMContext):
    await _process_callback_edit(query, state, "goal")


# endregion
