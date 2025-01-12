from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Habits


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
app = FastAPI()


class UserBase(BaseModel):
    user_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str

    class Config:
        orm_mode = True


@app.post("/users/")
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    new_user = User(
        user_id=user.user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
    )
    db.merge(new_user)
    db.commit()
    return {"message": "User created successfully"}


@app.post("/users/get_language")
async def get_language(user_id: int, db: Session = Depends(get_db)):
    lang = db.query(User.language).filter_by(user_id=user_id).scalar()
    return {"language": lang}


@app.post("/users/habit")
async def add_habit(user_id: int, habit_title: str, db: Session = Depends(get_db)):
    new_habit = Habits(user_id=user_id, habit_title=habit_title)
    db.add(new_habit)
    db.commit()
    return {"message": "Habit created successfully"}


@app.delete("/users/habit")
async def delete_habit(user_id: int, habit_title: str, db: Session = Depends(get_db)):
    db.query(Habits).filter_by(user_id=user_id, habit_title=habit_title).delete()
    db.commit()
    return {"message": "Habit deleted successfully"}


@app.post("/users/habits_list")
async def get_habits_list(user_id: int, list_type: str, db: Session = Depends(get_db)):
    logger.error(f"STARTING FUNC \n STARTING FUNC \n STARTING FUNC")
    if list_type == 'daily':
        habit_titles_and_counts = db.query(Habits.habit_title,
                                           Habits.days_count).filter_by(user_id=user_id,
                                                                        today_status=False).all()
    elif list_type == 'total':
        habit_titles_and_counts = db.query(Habits.habit_title,
                                           Habits.days_count).filter_by(user_id=user_id).all()
    habit_titles_and_counts_dict = [{"habit_title": habit[0], "days_count": habit[1]} for habit in
                                    habit_titles_and_counts]
    return habit_titles_and_counts_dict


@app.post("/users/habit_completed")
async def mark_habit(user_id: int, habit_title: str, db: Session = Depends(get_db)):
    habit = db.query(Habits).filter_by(user_id=user_id, habit_title=habit_title).first()
    if habit.days_count <= 20:
        db.query(Habits).filter_by(user_id=user_id,
                                   habit_title=habit_title).update({"today_status": True,
                                                                    "days_count":  Habits.days_count + 1})
        db.commit()
        return {"message": "Daily habit completed successfully"}
    else:
        db.query(Habits).filter_by(user_id=user_id, habit_title=habit_title).delete()
        db.commit()
        return {"message": "Habit completed successfully"}


@app.post("/reset_days")
async def reset_days(db: Session = Depends(get_db)):
    db.query(Habits).filter(Habits.today_status == False).update({
        "days_count": 0
    })
    db.commit()


@app.post("/users/all_habits")
async def get_all_habits(db: Session = Depends(get_db)):
    habits = db.query(Habits).all
    logger.info(f"\n\n ПРИВЫЧКИ: {habits}")
    return habits


@app.post("/users/update_reminder")
async def update_reminder(user_id: int, habit_title: str, reminder, db: Session = Depends(get_db)):
    db.query(Habits).filter_by(user_id=user_id,
                               habit_title=habit_title).update({"reminder": reminder})
    db.commit()
    return {"message": "Reminder updated"}
