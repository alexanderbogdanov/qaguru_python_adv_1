import json
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException

from models.User import User

app = FastAPI()

# users: list[User]
users: list[User] = []


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1 or user_id > len(users):
        return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users[user_id - 1]


@app.get("/api/users/", status_code=HTTPStatus.OK)
def get_users() -> list[User]:
    return users


if __name__ == "__main__":
    with open("users.json") as file:
        # users = json.load(file)
        users_data = json.load(file)
    # for user in users:
    #     User.model_validate(user)
    for user_data in users_data:
        validated_user = User.model_validate(user_data)  # Validate and transform
        users.append(validated_user)

    print("Users loaded successfully")
    uvicorn.run(app, host="localhost", port=8002)
