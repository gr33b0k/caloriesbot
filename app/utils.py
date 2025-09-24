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


def build_registration_message(data):
    lines = []
    lines.append("🎉 <b>Регистрация завершена!</b> 🎉\n")
    lines.append(f"🕰 Возраст: <code>{data['age']}</code>")
    lines.append(f"📏 Текущий рост: <code>{data['height']}</code>")
    lines.append(f"💪 Текущий вес: <code>{data['weight']}</code>")
    lines.append(
        f"🏃 Уровень активности: <code>{_match_activity(data['activity'])}</code>"
    )
    lines.append(f"🎯 Цель: <code>{_match_goal(data['goal'])}</code>")
    lines.append(
        f"🔥 Норма калорий для вашей цели: <code>{data['calorie_intake']} ккал</code>"
    )
    lines.append(f"🍗 Белки: <code>{data['proteins']} г</code>")
    lines.append(f"🥑 Жиры: <code>{data['fats']} г</code>")
    lines.append(f"🍚 Углеводы: <code>{data['carbons']} г</code>")
    lines.append(f"💧 Норма воды: <code>{data['water']} мл</code>\n")
    lines.append(
        "Важно: <i>расчёты КБЖУ носят рекомендательный характер и не заменяют консультацию врача/диетолога.</i>"
    )
    return "\n".join(lines)


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
