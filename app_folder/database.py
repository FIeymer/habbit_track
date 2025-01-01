import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Creating base class for models
Base = declarative_base()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Creating engine and session
engine = create_engine(
    "postgresql+psycopg2://admin:admin@postgres_db:5432/habits_db", echo=True
)
Session = sessionmaker(bind=engine)
session = Session()
