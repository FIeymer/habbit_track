from sqlalchemy import Column, String, Integer

from database import Base, engine


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language = Column(String)

Base.metadata.create_all(bind=engine)