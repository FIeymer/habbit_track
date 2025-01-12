import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from bot_api import bot, send_reminder

FASTAPI_URL = "http://habit_tracker_api:8000/users/"


def get_user_language(user_id: int) -> str:
    try:
        response = httpx.post(f"{FASTAPI_URL}get_language", params={"user_id": user_id})
        response.raise_for_status()
        return response.json().get("language")
    except httpx.RequestError as e:
        return f"Ошибка соединения с сервером: {e}"
    except httpx.HTTPStatusError as e:
        return f"Ошибка сервера: {e.response.text}"


def get_habits_list(user_id: int, list_type: str) -> list:
    try:
        response = httpx.post(f"{FASTAPI_URL}habits_list",
                              params={"user_id": user_id,
                                      "list_type": list_type})
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        bot.send_message(user_id, f"Ошибка соединения с сервером: {e}")
    except httpx.HTTPStatusError as e:
        bot.send_message(user_id, f"Ошибка сервера: {e.response.text}")


def get_all_habits() -> list:
    try:
        response = httpx.post(f"{FASTAPI_URL}all_habits")
        return response.json()
    except httpx.RequestError as e:
        pass
    except httpx.HTTPStatusError as e:
        pass


def schedule_user_reminders():
    habits = get_all_habits()
    for habit in habits:
        if habit["reminder_time"]:
            hour, minute = map(int, habit["reminder_time"].split(":"))
            job_id = f"reminder_{habit['habit_id']}"

            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

            scheduler.add_job(
                send_reminder,
                "cron",
                hour=hour,
                minute=minute,
                args=[habit["user_id"], habit['habit_title']],
                id=job_id
            )


scheduler = BackgroundScheduler()
