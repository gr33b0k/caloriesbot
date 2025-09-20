import app.keyboards as kb
import app.database.requests as rq
from app.utils import calculate_calories, build_registration_message
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


router = Router()


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


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.reply(
        "Здравствуйте! Давайте подберём Вашу норму калорий и КБЖУ. Сначала введите Ваш возраст.",
    )
    await state.update_data(telegram_id=message.from_user.id)
    await state.set_state(RegistrationStates.waiting_age)


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
