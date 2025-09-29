from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile"),
            InlineKeyboardButton(text="📊 Моё КБЖУ", callback_data="menu:daily_stats"),
        ],
        [
            InlineKeyboardButton(
                text="🍽 Питание на день", callback_data="menu:daily_nutrition"
            ),
            InlineKeyboardButton(
                text="💧 Выпить воды", callback_data="menu:track_water"
            ),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu:help"),
            InlineKeyboardButton(
                text="🔒 Конфиденциальность", callback_data="menu:privacy"
            ),
        ],
    ]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Изменить профиль", callback_data="profile:edit")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")],
    ]
)

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

edit_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👤 Имя", callback_data="edit:name")],
        [InlineKeyboardButton(text="🎂 Возраст", callback_data="edit:age")],
        [InlineKeyboardButton(text="📏 Рост", callback_data="edit:height")],
        [InlineKeyboardButton(text="⚖️ Вес", callback_data="edit:weight")],
        [InlineKeyboardButton(text="🏃 Активность", callback_data="edit:activity")],
        [InlineKeyboardButton(text="🎯 Цель", callback_data="edit:goal")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:profile")],
    ]
)

track_water_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="250 мл", callback_data="water:250")],
        [InlineKeyboardButton(text="500 мл", callback_data="water:500")],
        [InlineKeyboardButton(text="1 л", callback_data="water:1000")],
        [
            InlineKeyboardButton(
                text="Ввести своё значение", callback_data="water:custom"
            )
        ],
    ]
)


goal_change_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Похудение", callback_data="change_goal:loss")],
        [
            InlineKeyboardButton(
                text="Поддержание веса", callback_data="change_goal:maintain"
            )
        ],
        [
            InlineKeyboardButton(
                text="Набор мышечной массы", callback_data="change_goal:gain"
            )
        ],
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


def build_recipes_keyboard(recipes):
    recipes_builder = InlineKeyboardBuilder()
    for r in recipes:
        recipes_builder.button(
            text=f"{r.title} ({r.calories} ккал)", callback_data=f"pick_recipe:{r.id}"
        )
    recipes_builder.button(text="🔙 Назад", callback_data="pick_recipe:back")
    recipes_builder.adjust(1)
    return recipes_builder.as_markup()


def build_delete_recipe_keyboard(entries):
    builder = InlineKeyboardBuilder()
    for e in entries:
        builder.button(text=f"#{e.id}", callback_data=f"del_recipe:{e.id}")
    builder.adjust(3)
    return builder.as_markup()
