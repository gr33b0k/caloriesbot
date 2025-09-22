from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


sex_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="sex:male")],
        [InlineKeyboardButton(text="Женский", callback_data="sex:female")],
    ]
)

activity_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Сидячий образ жизни",
                callback_data="activity:inactive",
            )
        ],
        [
            InlineKeyboardButton(
                text="Легкая активность", callback_data="activity:light"
            )
        ],
        [
            InlineKeyboardButton(
                text="Умеренная активность",
                callback_data="activity:moderate",
            )
        ],
        [
            InlineKeyboardButton(
                text="Активный образ жизни", callback_data="activity:high"
            )
        ],
        [
            InlineKeyboardButton(
                text="Очень активный образ жизни", callback_data="activity:very-high"
            )
        ],
    ]
)


goal_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Похудение", callback_data="goal:loss")],
        [InlineKeyboardButton(text="Поддержание веса", callback_data="goal:maintain")],
        [InlineKeyboardButton(text="Набор мышечной массы", callback_data="goal:gain")],
    ]
)


track_water_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="250 мл", callback_data="water:250")],
        [InlineKeyboardButton(text="500 мл", callback_data="water:500")],
        [InlineKeyboardButton(text="1 л", callback_data="water:1000")],
        [InlineKeyboardButton(text="Ввести своё значение", callback_data="water:custom")],
    ]
)


goal_change_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Похудение", callback_data="change_goal:loss")],
        [InlineKeyboardButton(text="Поддержание веса", callback_data="change_goal:maintain")],
        [InlineKeyboardButton(text="Набор мышечной массы", callback_data="change_goal:gain")],
    ]
)


change_goal_button_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сменить цель", callback_data="change_goal:open")],
    ]
)


recipes_categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Завтрак", callback_data="recipes:breakfast")],
        [InlineKeyboardButton(text="Обед", callback_data="recipes:lunch")],
        [InlineKeyboardButton(text="Полдник", callback_data="recipes:snack")],
        [InlineKeyboardButton(text="Ужин", callback_data="recipes:dinner")],
    ]
)