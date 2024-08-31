from http import HTTPStatus
from typing import Iterable, Type, List

from fastapi import APIRouter, HTTPException, Depends
from app.database import users
from sqlmodel import Session
from app.models.User import User, UserCreate, UserUpdate
from app.database.engine import get_session, engine

router = APIRouter(prefix="/api/users")


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    user = users.get_user(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.get("/", status_code=HTTPStatus.OK)
def get_users(session: Session = Depends(get_session)) -> List[User]: # the return type will change later
    return users.get_users()


# @router.post("/", status_code=HTTPStatus.CREATED)
# def create_user(user: UserCreate, session: Session = Depends(get_session)) -> User:
#     new_user = User.model_validate(user)
#     return users.create_user(new_user)

@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)) -> User:
    """
    Create a new user based on the validated UserCreate model.
    Returns the created User instance.
    """
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar=str(user.avatar)  # Convert HttpUrl to str for database storage
    )
    return users.create_user(new_user)


# @router.patch("/{user_id}", status_code=HTTPStatus.OK)
# def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session)) -> User:
#     if user_id < 1:
#         raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
#     return users.update_user(user_id, user)

def update_user(user_id: int, user: UserUpdate) -> User:
    """
    Update an existing user's details. Raise an HTTP 404 error if the user is not found.
    Returns the updated User instance.
    """
    with Session(engine) as session:
        # Retrieve the user instance from the database
        db_user: User | None = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        # Update the db_user instance with the non-null fields from user
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        # Return the updated User instance
        return db_user


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    users.delete_user(user_id)
    return {"message": "User deleted successfully"}

