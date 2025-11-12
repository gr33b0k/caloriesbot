from typing import Union
import app.keyboards as kb
import app.database.requests as rq
from app.utils import (
    build_daily_nutrition_message,
    build_daily_stats_message,
    build_help_message,
    build_menu_message,
    build_not_registered_message,
    build_profile_message,
    build_recipe_message,
    calculate_calories,
)
from app.constants import *
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

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


# region Registration


@router.message(CommandStart())
@router.callback_query(lambda c: c.data and c.data == "start:reregister")
async def start_command(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, Message):
        user_id = update.from_user.id
        reply_method = update.answer
    else:
        user_id = update.from_user.id
        reply_method = update.message.edit_text
        await update.answer()

    user = await rq.get_user(user_id)

    if isinstance(update, CallbackQuery):
        await reply_method(
            "🔄 <b>Начинаем регистрацию заново</b>\n\n"
            "Пожалуйста, напишите своё имя:",
            parse_mode="HTML",
        )
        await state.update_data(telegram_id=user_id, user_exists=True)
        await state.set_state(RegistrationStates.waiting_name)
        return

    if user and isinstance(update, Message):
        await reply_method(
            "✨ Вы уже проходили регистрацию ранее\n\nЧто хотите сделать?",
            parse_mode="HTML",
            reply_markup=kb.start_choice_keyboard,
        )
        await state.clear()
        return

    await state.clear()
    await reply_method("Давайте познакомимся! 🙂 Пожалуйста, напишите своё имя.")
    await state.update_data(telegram_id=user_id, user_exists=False)
    await state.set_state(RegistrationStates.waiting_name)


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
@router.callback_query(lambda c: c.data and c.data == "start:menu")
async def menu_command(update: Union[Message, CallbackQuery]):
    if isinstance(update, Message):
        message = update
        user_id = update.from_user.id
    else:
        message = update.message
        user_id = update.from_user.id
        await update.answer()

    user = await rq.get_user(user_id)
    if not user:
        if isinstance(update, Message):
            await message.answer(build_not_registered_message(), parse_mode="HTML")
        else:
            await message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    message_text = build_menu_message(False)

    if isinstance(update, Message):
        await message.answer(
            message_text, reply_markup=kb.menu_keyboard, parse_mode="HTML"
        )
    else:
        await message.edit_text(
            message_text, reply_markup=kb.menu_keyboard, parse_mode="HTML"
        )


@router.callback_query(lambda c: c.data and c.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery):
    await query.answer()
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return
    message_text = build_menu_message(False)
    await query.message.edit_text(
        message_text, parse_mode="HTML", reply_markup=kb.menu_keyboard
    )


@router.callback_query(lambda c: c.data and c.data == "menu:profile")
async def menu_profile(query: CallbackQuery):
    await query.answer()
    user_id = query.from_user.id
    user_data = await rq.get_user(user_id)
    if not user_data:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return
    message_text = build_profile_message(user_data)
    await query.message.edit_text(
        message_text, parse_mode="HTML", reply_markup=kb.profile_keyboard
    )


@router.callback_query(lambda c: c.data and c.data == "menu:daily_stats")
async def menu_daily_stats(query: CallbackQuery):
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    meals_sum = await rq.get_today_recipes_sum(query.from_user.id)
    water_sum = await rq.get_today_water_sum(query.from_user.id)

    message_text = build_daily_stats_message(user, meals_sum, water_sum)

    await query.message.edit_text(
        message_text, reply_markup=kb.daily_stats_keyboard, parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data == "menu:daily_nutrition")
async def menu_daily_nutrition(query: CallbackQuery):
    await query.answer()
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return
    meals_list = await rq.list_selected_recipes(query.from_user.id)
    message_text = build_daily_nutrition_message(meals_list)
    await query.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=kb.build_meals_keyboard(set(meals_list)),
    )


@router.callback_query(lambda c: c.data and c.data == "menu:track_water")
async def menu_track_water(query: CallbackQuery):
    user = await rq.get_user(query.from_user.id)
    if user:
        await query.message.edit_text(
            "💧 <b>Отслеживание воды</b>\n\n"
            f"📊 <b>Ваша дневная норма:</b> <code>{user.water} мл</code>\n\n"
            "➕ <i>Выберите объём воды или введите свой</i>",
            reply_markup=kb.track_water_keyboard,
            parse_mode="HTML",
        )
    else:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")


@router.message(Command("privacy"))
@router.callback_query(lambda c: c.data and c.data == "menu:privacy")
async def menu_privacy(update: Union[Message, CallbackQuery]):
    if isinstance(update, Message):
        message = update
        user_id = update.from_user.id
    else:
        message = update.message
        user_id = update.from_user.id
        await update.answer()

    user_exists = await rq.user_exists(user_id)
    message_text = (
        "<b>🔐 Политика конфиденциальности</b>\n\n"
        "✨ <b>Мы заботимся о вашей конфиденциальности</b> ✨\n\n"
        "📋 <u>Какие данные мы храним:</u>\n"
        "📊 Информацию, которую вы добровольно предоставляете\n"
        "🧮 Результаты расчетов КБЖУ\n\n"
        "🎯 <u>Для чего используем:</u>\n"
        "✅ Исключительно для расчетов калорийности и БЖУ\n\n"
        "🛡️ <u>Гарантии безопасности:</u>\n"
        "🔒 Ваши данные защищены\n"
        "🙅‍♂️ Не передаются третьим лицам\n"
        "📝 Вы всегда можете запросить удаление данных\n\n"
        "🌟 <i>Спасибо, что доверяете нам!</i> 🌟"
    )
    if isinstance(update, Message):
        await message.answer(message_text, parse_mode="HTML")
    else:
        await message.edit_text(
            message_text,
            reply_markup=kb.back_to_menu_keyboard if user_exists else None,
            parse_mode="HTML",
        )


@router.message(Command("help"))
@router.callback_query(lambda c: c.data and c.data == "menu:help")
async def menu_help(update: Union[Message, CallbackQuery]):
    if isinstance(update, Message):
        message = update
        user_id = update.from_user.id
    else:
        message = update.message
        user_id = update.from_user.id
        await update.answer()

    user_exists = await rq.user_exists(user_id)
    if isinstance(update, Message):
        await message.answer(build_help_message(user_exists), parse_mode="HTML")
    else:
        await message.edit_text(
            build_help_message(user_exists),
            reply_markup=kb.back_to_menu_keyboard if user_exists else None,
            parse_mode="HTML",
        )


# endregion


# region Profile


@router.callback_query(lambda c: c.data == "profile:edit")
async def edit_profile(query: CallbackQuery):
    await query.answer()
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return
    await query.message.edit_text(
        "Выберите, что Вы хотите поменять:", reply_markup=kb.edit_profile_keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("edit:"))
async def edit_field_selection(query: CallbackQuery, state: FSMContext):
    await query.answer()
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

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


# region Recipes


@router.callback_query(lambda c: c.data and c.data.startswith("recipes:"))
async def recipes_by_category(query: CallbackQuery):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, category, menu_item = query.data.split(":")
    if category == "plan":
        await query.message.edit_text(
            "Выберите приём пищи:",
            reply_markup=kb.build_recipes_categories_keyboard(menu_item),
        )
        return
    max_cal = user.calorie_intake
    recipes = await rq.get_recipes_by_category_and_limit(category, max_cal)
    if not recipes:
        await query.message.edit_text(
            "Подходящих рецептов не найдено", reply_markup=kb.back_to_menu_keyboard
        )
        return

    message_text = build_recipe_message(recipes[0])
    await query.message.edit_text(
        message_text,
        reply_markup=kb.build_recipes_keyboard(category, 0, len(recipes), menu_item),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("recipe_nav:"))
async def navigate_recipes(query: CallbackQuery):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, category, index, menu_item = query.data.split(":")
    index = int(index)

    recipes = await rq.get_recipes_by_category_and_limit(category, user.calorie_intake)
    total = len(recipes)

    if index < 0 or index >= total:
        return

    message_text = build_recipe_message(recipes[index])

    await query.message.edit_text(
        message_text,
        reply_markup=kb.build_recipes_keyboard(category, index, total, menu_item),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("pick_recipe:"))
async def pick_recipe(query: CallbackQuery):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, recipe_id, menu_item = query.data.split(":")
    await rq.add_recipe_selection(query.from_user.id, int(recipe_id))
    await query.message.edit_text(
        "Вы успешно добавили рецепт!\n\nВыберите приём пищи:",
        reply_markup=kb.build_recipes_categories_keyboard(menu_item),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("show_recipe:"))
async def show_recipe(query: CallbackQuery):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, recipe_id = query.data.split(":")
    recipe = await rq.get_recipe(int(recipe_id))
    message_text = build_recipe_message(recipe)
    await query.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=kb.build_delete_recipe_keyboard(recipe_id),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("del_recipe:"))
async def delete_recipe_entry(query: CallbackQuery):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, entry_id = query.data.split(":")
    await rq.delete_selected_recipe(int(entry_id), query.from_user.id)
    meals_list = await rq.list_selected_recipes(query.from_user.id)
    message_text = build_daily_nutrition_message(meals_list)
    await query.message.edit_text(
        message_text,
        reply_markup=kb.build_meals_keyboard(meals_list),
        parse_mode="HTML",
    )


# endregion


# region Water


@router.callback_query(lambda c: c.data and c.data.startswith("water:"))
async def water_choice(query: CallbackQuery, state: FSMContext):
    await query.answer()

    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.edit_text(build_not_registered_message(), parse_mode="HTML")
        return

    _, value = query.data.split(":")
    if value == "custom":
        await query.message.edit_text(
            "📝 <i>Введите объём воды в мл (целое число):</i>\n"
            "Например: <code>250</code>",
            parse_mode="HTML",
            reply_markup=kb.back_to_menu_keyboard,
        )
        await state.set_state(WaterStates.waiting_custom_value)
        return
    amount_ml = int(value)
    await rq.add_water_log(query.from_user.id, amount_ml)
    try:
        await query.message.edit_text(
            "✅ <b>Приём воды зарегистрирован</b>\n\n"
            f"💧 Выпито: <code>{amount_ml} мл</code>\n\n"
            "<i>➕ Выберите объём воды или введите свой</i>",
            parse_mode="HTML",
            reply_markup=kb.track_water_keyboard,
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise e


@router.message(WaterStates.waiting_custom_value)
async def water_custom_value(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer(
            "❌ <b>Неверный формат</b>\n\n"
            "📝 <i>Пожалуйста, введите целое число в миллилитрах:</i>\n"
            "Например: <code>300</code>"
        )
        return
    amount_ml = int(text)
    await rq.add_water_log(message.from_user.id, amount_ml)
    await message.answer(
        "✅ <b>Приём воды зарегистрирован</b>\n\n"
        f"💧 Выпито: <code>{amount_ml} мл</code>\n\n"
        "<i>➕ Выберите объём воды или введите свой</i>",
        parse_mode="HTML",
        reply_markup=kb.track_water_keyboard,
    )
    await state.clear()


# endregion
