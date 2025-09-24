import app.keyboards as kb
import app.database.requests as rq
from app.utils import calculate_calories, build_registration_message, match_activity
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()


# region States


class RegistrationStates(StatesGroup):
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


# endregion


# region General commands


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.reply(
        "Здравствуйте! Давайте подберём Вашу норму калорий и КБЖУ. Сначала введите Ваш возраст.",
    )
    await state.update_data(telegram_id=message.from_user.id)
    await state.set_state(RegistrationStates.waiting_age)


@router.message(Command("recommend_food"))
async def handleRecommendFood(message: Message):
    await message.answer(
        "Посоветуй что поесть 🍽\nНапишите время приёма пищи (завтрак/обед/ужин) — я подскажу идеи."
    )


@router.message(Command("plan"))
async def handlePlan(message: Message):
    await message.answer(
        'Планирование питания 📅\nОпишите период (например: "на неделю") и предпочтения.'
    )


@router.message(Command("add_meal"))
async def handleAddMeal(message: Message):
    await message.answer(
        'Добавить еду 🍽\nНапишите, что вы съели и сколько (например: "овсянка 60 г").'
    )


@router.message(Command("delete_meals"))
async def handleDeleteMeals(message: Message):
    entries = await rq.list_selected_recipes(message.from_user.id)
    if not entries:
        await message.answer("У вас нет добавленных рецептов")
        return
    builder = InlineKeyboardBuilder()
    for e in entries:
        builder.button(text=f"#{e.id}", callback_data=f"del_recipe:{e.id}")
    builder.adjust(3)
    await message.answer(
        "Удалить приём пищи 🗑\nВыберите запись для удаления:",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("show_today_calories"))
async def handleShowTodayCalories(message: Message):
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
async def handleHelp(message: Message):
    await message.answer(
        "Помощь 🛠\nДоступные команды:\n"
        "/recipes, /add_meal, /delete_meals, /show_today_calories, /recommend_food,\n"
        "/plan, /track_water, /my_goal, /change_products, /help, /privacy"
    )


@router.message(Command("privacy"))
async def handlePrivacy(message: Message):
    await message.answer(
        "Политика конфиденциальности\nМы храним только данные, которые вы нам отправляете, для расчётов КБЖУ."
    )


@router.message(Command("change_products"))
async def handleChangeProducts(message: Message):
    await message.answer(
        'Замена продуктов 🔄\nНапишите продукт и альтернативу (например: "майонез → греческий йогурт").'
    )


# endregion


# region Recipes


@router.message(Command("recipes"))
async def handleRecipes(message: Message):
    await rq.seed_recipes_if_empty()
    await message.answer(
        "Выберите приём пищи:", reply_markup=kb.recipes_categories_keyboard
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
    builder = InlineKeyboardBuilder()
    for r in recipes:
        builder.button(
            text=f"{r.title} ({r.calories} ккал)", callback_data=f"pick_recipe:{r.id}"
        )
    builder.adjust(1)
    await query.message.answer("Выберите рецепт:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data and c.data.startswith("pick_recipe:"))
async def pick_recipe(query: CallbackQuery):
    await query.answer()
    _, recipe_id = query.data.split(":")
    await rq.add_recipe_selection(query.from_user.id, int(recipe_id))
    await query.message.answer("Вы успешно добавили рецепт!")


@router.callback_query(lambda c: c.data and c.data.startswith("del_recipe:"))
async def delete_recipe_entry(query: CallbackQuery):
    await query.answer()
    _, entry_id = query.data.split(":")
    await rq.delete_selected_recipe(int(entry_id), query.from_user.id)
    await query.message.answer("Рецепт удалён")


# endregion


# region Water


@router.message(Command("track_water"))
async def handleTrackWater(message: Message):
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


# region Goal


@router.message(Command("my_goal"))
async def handleMyGoal(message: Message):
    user = await rq.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return
    await message.answer(
        "Моя цель 🎉\n"
        f"Возраст: {user.age}\n"
        f"Рост: {user.height}\n"
        f"Вес: {user.weight}\n"
        f"Активность: {match_activity(user.activity)}\n"
        f"Целевая калорийность: {user.calorie_intake} ккал",
        reply_markup=kb.change_goal_button_kb,
    )


@router.callback_query(lambda c: c.data == "change_goal:open")
async def open_change_goal(query: CallbackQuery):
    await query.answer()
    await query.message.answer(
        "Выберите новую цель:", reply_markup=kb.goal_change_keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("change_goal:"))
async def change_goal_apply(query: CallbackQuery):
    await query.answer()
    _, new_goal = query.data.split(":")
    if new_goal == "open":
        return
    user = await rq.get_user(query.from_user.id)
    if not user:
        await query.message.answer("Сначала пройдите регистрацию: /start")
        return
    data = {
        "age": user.age,
        "sex": user.sex,
        "height": user.height,
        "weight": user.weight,
        "activity": user.activity,
        "goal": new_goal,
    }
    results = calculate_calories(data)
    await rq.update_user_goal(
        query.from_user.id,
        goal=new_goal,
        calorie_intake=results["calorie_intake"],
        proteins=results["proteins"],
        fats=results["fats"],
        carbons=results["carbons"],
    )
    await query.message.answer(
        "Цель обновлена ✅\n"
        f"Новая целевая калорийность: {results['calorie_intake']} ккал\n"
        f"Белки: {results['proteins']} г, Жиры: {results['fats']} г, Углеводы: {results['carbons']} г"
    )


# endregion


# region Registration


@router.message(RegistrationStates.waiting_age)
async def age_callback(message: Message, state: FSMContext):
    age_str = message.text
    try:
        age_int = int(age_str)
    except ValueError:
        await message.answer("Пожалуйста, отправьте число в диапазоне 16-100")
        return
    if not (16 <= age_int <= 100):
        await message.answer("Пожалуйста, отправьте число в диапазоне 16-100")
        return
    await state.update_data(age=age_int)
    await message.answer("Выберите Ваш пол.", reply_markup=kb.sex_keyboard)
    await state.set_state(RegistrationStates.waiting_sex)


@router.callback_query(lambda c: c.data and c.data.startswith("sex:"))
async def sex_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, sex = query.data.split(":")
    await state.update_data(sex=sex)
    await query.message.answer("Введите Ваш рост в сантиметрах")
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
    await message.answer("Введите ваш вес в килограммах")
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
        "Выберите ваш уровень активности", reply_markup=kb.activity_keyboard
    )
    await state.set_state(RegistrationStates.waiting_activity)


@router.callback_query(lambda c: c.data and c.data.startswith("activity:"))
async def cb_activity(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, activity = query.data.split(":")
    await state.update_data(activity=activity)
    await query.message.answer("Выберите вашу цель", reply_markup=kb.goal_keyboard)
    await state.set_state(RegistrationStates.waiting_goal)


@router.callback_query(lambda c: c.data and c.data.startswith("goal:"))
async def goal_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    _, goal = query.data.split(":")
    await state.update_data(goal=goal)
    data = await state.get_data()
    results = calculate_calories(data)
    combined_data = {**data, **results}
    message_text = build_registration_message(combined_data)
    await rq.set_user(combined_data)
    await query.message.answer(message_text, parse_mode="HTML")
    await state.clear()


# endregion
