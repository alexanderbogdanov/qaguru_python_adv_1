import json
import logging
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi_pagination import Params, Page, paginate, add_pagination
from contextlib import asynccontextmanager

from models.AppStatus import AppStatus
from models.User import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    with open("users.json") as file:
        users_data = json.load(file)

    for user_data in users_data:
        try:
            validated_user = User.model_validate(user_data)
            users.append(validated_user)
        except Exception as e:
            logger.error(f"Validation error for user data: {user_data}, error: {e}")

    logger.info("Users loaded successfully")
    logger.info(f"Total users loaded: {len(users)}")
    yield


app = FastAPI(lifespan=lifespan)

users: list[User] = []


@app.get("/api/status", response_model=AppStatus, status_code=HTTPStatus.OK)
def status():
    return AppStatus(users=bool(users))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users[user_id - 1]


@app.get("/api/users/", response_model=Page[User], status_code=HTTPStatus.OK)
def get_users(page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=100)) -> Page[User]:
    params = Params(page=page, size=size)
    logger.info(f"Params received: Page number: {params.page}, Page size: {params.size}")

    paginated_users = paginate(users, params)

    logger.info(f"Paginated users count: {len(paginated_users.items)}")
    for user in paginated_users.items:
        logger.info(f"Paginated user: {user}")

    return paginated_users


if __name__ == "__main__":
    add_pagination(app)
    uvicorn.run(app, host="localhost", port=8002)
