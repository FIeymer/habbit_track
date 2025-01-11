import httpx
from apscheduler.schedulers.background import BackgroundScheduler

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


def reset_days():
    try:
        response = httpx.post("http://habit_tracker_api:8000/reset_days")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(e)
    except httpx.HTTPStatusError as e:
        logger.error(e)


scheduler = BackgroundScheduler()
scheduler.add_job(reset_days, 'cron', hour=0)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())
