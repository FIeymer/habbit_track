from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Habits

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
    if list_type == 'daily':
        db.query(Habits).filter_by(user_id=user_id, today_status=False).all()
    elif list_type == 'total':
        db.query(Habits).filter_by(user_id=user_id).all()
    habit_titles = [title[0] for title in db.query(Habits.habit_title).filter_by(user_id=user_id).all()]
    return habit_titles


@app.post("/users/habit_completed")
async def mark_habit(user_id: int, habit_title: str, db: Session = Depends(get_db)):
    db.query(Habits).filter_by(user_id=user_id,
                               habit_title=habit_title).update({"today_status": True})
    db.commit()
    return {"message": "Habit completed successfully"}
