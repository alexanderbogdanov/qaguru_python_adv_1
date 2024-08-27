
# This part of the code is bringing in (importing) tools and packages that help our program do different tasks.
import json  # This helps us work with data in JSON format, which is a way to organize information like a list or dictionary.
import logging  # This helps us keep a record of what our program is doing, like a diary.
from http import HTTPStatus  # This helps us use specific numbers to represent different outcomes when people interact with our program. For example, 200 means "everything is okay."

import uvicorn  # This helps us run our program so other people can use it on their computers.
from fastapi import FastAPI, HTTPException, Query  # These tools help us create a web service that can do different tasks, like give information to users.
from fastapi_pagination import Params, Page, paginate, add_pagination  # These tools help us show information in pieces or pages, instead of all at once.
from contextlib import asynccontextmanager  # This helps us manage some actions before and after our main task, like preparing or cleaning up.

from app.models.AppStatus import AppStatus  # This tells our program to use a specific format for showing if it's working okay.
from app.models.User import User  # This tells our program to use a specific format for showing user information.

# This section of the code is defining a special setup process that runs when we start our program.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # When the program starts, we open a file that contains user information.
    with open("../users.json") as file:
        users_data = json.load(file)  # We load the user information into our program.

    # We go through each user's information to make sure it fits our format.
    for user_data in users_data:
        try:
            validated_user = User(**user_data)  # We check if the user information is correct.
            users.append(validated_user)  # If it's correct, we add it to our list of users.
        except Exception as e:
            # If there's a mistake in the user information, we write it down in our diary (log).
            logger.error(f"Validation error for user data: {user_data}, error: {e}")

    # We write down in our diary that the users have been loaded successfully.
    logger.info("Users loaded successfully")
    # We also note how many users we have.
    logger.info(f"Total users loaded: {len(users)}")
    yield  # This marks the end of the setup process.

# This part creates our web service using FastAPI, a tool that helps us build web applications.
app = FastAPI(lifespan=lifespan)

# Here we create an empty list where we'll store all our users.
users: list[User] = []

# This is setting up our diary (log) to keep track of what happens in our program.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This part defines what happens when someone asks for the status of our service.
@app.get("/api/status", response_model=AppStatus, status_code=HTTPStatus.OK)
def status():
    # We check if there are users in our list and return whether the service is working (True) or not (False).
    return AppStatus(users=bool(users))

# This part defines what happens when someone asks for information about a specific user.
@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    # If the user ID is less than 1, it means the request is incorrect.
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    # If the user ID is higher than the number of users we have, the user doesn't exist.
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    # Otherwise, we return the information of the user.
    return users[user_id - 1]

# This part defines what happens when someone asks for a list of users.
@app.get("/api/users/", response_model=Page[User], status_code=HTTPStatus.OK)
def get_users(page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=100)) -> Page[User]:
    # We set up the rules for how many users to show on each page.
    params = Params(page=page, size=size)
    # We write down what page number and size the person asked for.
    logger.info(f"Params received: Page number: {params.page}, Page size: {params.size}")

    # We organize the users into pages based on the rules set up earlier.
    paginated_users = paginate(users, params)

    # We write down how many users are being shown on this page.
    logger.info(f"Paginated users count: {len(paginated_users.items)}")
    # For each user on this page, we write down their information.
    for user in paginated_users.items:
        logger.info(f"Paginated user: {user}")

    # Finally, we return the list of users for this page.
    return paginated_users

# This part runs the web service so other people can use it by going to a specific address (localhost:8002).
if __name__ == "__main__":
    add_pagination(app)  # We add the ability to show information in pages.
    uvicorn.run(app, host="localhost", port=8002)  # We start the service so it listens on port 8002.
