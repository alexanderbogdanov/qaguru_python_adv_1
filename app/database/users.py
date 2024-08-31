from http import HTTPStatus
from typing import Iterable, Type, List, Optional

from fastapi import HTTPException

from app.models.User import User, UserUpdate
from sqlmodel import Session, select
from app.database.engine import engine


def get_user(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id)


def get_users() -> List[User]:
    with Session(engine) as session:
        statement = select(User)
        result = session.exec(statement).all()
        return list(result)


def create_user(user: User) -> User:
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user(user_id: int, user: UserUpdate) -> User: # need to fix
    with Session(engine) as session:
        db_user: User | None = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        session.delete(user)
        session.commit()
