from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base, engine


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language = Column(String)
    habits = relationship("Habits", back_populates="author")


class Habits(Base):
    __tablename__ = "habits"

    habit_id = Column(Integer, primary_key=True)
    habit_title = Column(String)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    author = relationship("User", back_populates="habits")


Base.metadata.create_all(bind=engine)