import json
import logging
import os

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi_pagination import add_pagination

from app.routers import status, users
from app.models.User import User
from app.database import users_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    file_path = os.path.join(os.path.dirname(__file__), "..", "users.json")
    with open(file_path) as file:
        raw_users = json.load(file)

    for user_data in raw_users:
        try:
            validated_user = User.model_validate(user_data)  # Validate individual user
            users_db.append(validated_user)
        except Exception as e:
            logger.error(f"Validation error for user data: {user_data}, error: {e}")

    logger.info("Users loaded successfully")
    logger.info(f"Total users loaded: {len(users_db)}")
    yield

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
app.include_router(status.router)
app.include_router(users.router)

if __name__ == "__main__":
    add_pagination(app)
    uvicorn.run(app, host="localhost", port=8002)
