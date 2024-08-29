from http import HTTPStatus
from typing import Iterable, Type

from fastapi import APIRouter, HTTPException
from app.database import users
from app.models.User import User, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users")


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    user = users.get_user(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.get("/", status_code=HTTPStatus.OK)
def get_users() -> Iterable[User]: # the return type will change later
    return users.get_users()


@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: User) -> User:
    UserCreate.model_validate(user)
    return users.create_user(user)

@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User) -> Type[User]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    UserUpdate.model_validate(user)
    return users.update_user(user_id, user)

@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    users.delete_user(user_id)
    return {"message": "User deleted successfully"}

