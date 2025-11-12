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
            InlineKeyboardButton(text="❓ Помощь", callback_data="menu:help"),
            InlineKeyboardButton(
                text="🔒 Конфиденциальность", callback_data="menu:privacy"
            ),
        ],
    ]
)

back_to_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✍ Изменить профиль", callback_data="profile:edit")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ]
)

daily_stats_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗓 Запланировать прием пищи",
                callback_data="recipes:plan:daily_stats",
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ]
)

edit_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Имя", callback_data="edit:name"),
            InlineKeyboardButton(text="🚻 Пол", callback_data="edit:sex"),
        ],
        [
            InlineKeyboardButton(text="🎂 Возраст", callback_data="edit:age"),
            InlineKeyboardButton(text="📏 Рост", callback_data="edit:height"),
        ],
        [
            InlineKeyboardButton(text="⚖️ Вес", callback_data="edit:weight"),
            InlineKeyboardButton(text="🏃 Активность", callback_data="edit:activity"),
        ],
        [
            InlineKeyboardButton(text="🎯 Цель", callback_data="edit:goal"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="menu:profile"),
        ],
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

track_water_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💦 250 мл", callback_data="water:250")],
        [InlineKeyboardButton(text="🚰 500 мл", callback_data="water:500")],
        [InlineKeyboardButton(text="⛲️ 1 л", callback_data="water:1000")],
        [
            InlineKeyboardButton(
                text="✍️ Ввести своё значение", callback_data="water:custom"
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
    ]
)

start_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔄 Пройти регистрацию заново", callback_data="start:reregister"
            )
        ],
        [InlineKeyboardButton(text="🚀 Перейти в меню", callback_data="start:menu")],
    ]
)


def back_to_menu_item_button(menu_item):
    return (
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"menu:{menu_item}",
        ),
    )


def build_recipes_categories_keyboard(menu_item):
    categories_builder = InlineKeyboardBuilder()
    categories_builder.add(
        InlineKeyboardButton(
            text="🥞 Завтрак", callback_data=f"recipes:breakfast:{menu_item}"
        ),
        InlineKeyboardButton(
            text="🍱 Обед", callback_data=f"recipes:lunch:{menu_item}"
        ),
        InlineKeyboardButton(
            text="🧆 Ужин", callback_data=f"recipes:dinner:{menu_item}"
        ),
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"menu:{menu_item}",
        ),
    )
    categories_builder.adjust(1)

    return categories_builder.as_markup()


def build_delete_recipe_keyboard(recipe_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить", callback_data=f"del_recipe:{recipe_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад", callback_data=f"menu:daily_nutrition"
                ),
            ],
        ]
    )

    return keyboard


def build_recipes_keyboard(category: str, index: int, total: int, menu_item):
    buttons = []
    if index > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"recipe_nav:{category}:{index-1}:{menu_item}",
            )
        )
    if index < total - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"recipe_nav:{category}:{index+1}:{menu_item}",
            )
        )
    return (
        InlineKeyboardMarkup(
            inline_keyboard=[
                buttons,
                [
                    InlineKeyboardButton(
                        text="Добавить в корзину",
                        callback_data=f"pick_recipe:{index}:{menu_item}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Назад", callback_data=f"recipes:plan:{menu_item}"
                    )
                ],
            ]
        )
        if buttons
        else None
    )


def build_meals_keyboard(meals):
    recipes_builder = InlineKeyboardBuilder()
    if meals:
        for meal in meals:
            recipes_builder.button(
                text=f"{meal.title} ({meal.calories} ккал)",
                callback_data=f"show_recipe:{meal.id}",
            )
    else:
        recipes_builder.button(
            text="🗓 Запланировать прием пищи",
            callback_data="recipes:plan:daily_nutrition",
        )
    recipes_builder.button(text="🔙 Назад", callback_data="back_to_menu")
    recipes_builder.adjust(1)
    return recipes_builder.as_markup()
