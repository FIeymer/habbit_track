import httpx

FASTAPI_URL = "http://habit_tracker_api:8000/users/"

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


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
        return f"Ошибка соединения с сервером: {e}"
    except httpx.HTTPStatusError as e:
        return f"Ошибка сервера: {e.response.text}"


def get_all_habits() -> list:
    try:
        response = httpx.post(f"{FASTAPI_URL}all_habits")
        return response.json()
    except httpx.RequestError as e:
        logger.error(e)
    except httpx.HTTPStatusError as e:
        logger.error(e)


def get_habit_id(habit_title, user_id):
    try:
        response = httpx.post(f"{FASTAPI_URL}habit_id", params={"user_id": user_id,
                                      "habit_title": habit_title})
        return response.json()
    except httpx.RequestError as e:
        logger.error(e)
    except httpx.HTTPStatusError as e:
        logger.error(e)


def check_habit_status(user_id, habit_title):
    try:
        response = httpx.post(f"{FASTAPI_URL}check_habit_status", params={"user_id": user_id,
                                      "habit_title": habit_title})
        return response.json()
    except httpx.RequestError as e:
        logger.error(e)
    except httpx.HTTPStatusError as e:
        logger.error(e)
