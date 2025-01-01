from sqlalchemy import Column, String

from database import Base, engine


class User(Base):
    __tablename__ = "users"

    user_id = Column(primary_key=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language = Column(String)




Base.metadata.create_all(bind=engine)