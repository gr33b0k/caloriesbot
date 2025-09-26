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
