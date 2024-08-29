import os

from sqlalchemy.orm import Session
from sqlmodel import create_engine, SQLModel, text

engine = create_engine(
    os.getenv("DATABASE_ENGINE"),
    pool_size=int(os.getenv("DATABASE_CONNECTION_POOL_SIZE", 10))
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def check_if_db_available() -> bool:
    try:
        with Session(engine) as session:
            session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
