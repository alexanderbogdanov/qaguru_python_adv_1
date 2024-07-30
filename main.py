import json
import logging
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException

from models.User import User

app = FastAPI()

# users: list[User]
users: list[User] = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1 or user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users[user_id - 1]


@app.get("/api/users/", status_code=HTTPStatus.OK)
def get_users() -> list[User]:
    return users


if __name__ == "__main__":
    with open("users.json") as file:
        users_data = json.load(file)
    for user_data in users_data:
        try:
            validated_user = User.model_validate(user_data)  # Validate and transform
            users.append(validated_user)
        except Exception as e:
            logger.error(f"Validation error for user data: {user_data}, error: {e}")

    logger.info("Users loaded successfully")
    uvicorn.run(app, host="localhost", port=8002)
