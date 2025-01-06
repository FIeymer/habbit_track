from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, session, get_db
from models import User

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
    #db.refresh(new_user)
    return {"message": "User created successfully"}
