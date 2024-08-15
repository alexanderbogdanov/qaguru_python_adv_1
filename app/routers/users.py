import logging
from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Query
from fastapi_pagination import Params, Page, paginate, add_pagination
from app.database import users_db
from app.models.User import User

router = APIRouter(prefix="/api/users")


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    if user_id > len(users_db):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users_db[user_id - 1]


@router.get("/", response_model=Page[User], status_code=HTTPStatus.OK)
def get_users(page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=100)) -> Page[User]:
    params = Params(page=page, size=size)
    logger.info(f"Params received: Page number: {params.page}, Page size: {params.size}")

    paginated_users = paginate(users_db, params)

    logger.info(f"Paginated users count: {len(paginated_users.items)}")
    for user in paginated_users.items:
        logger.info(f"Paginated user: {user}")

    return paginated_users


logger = logging.getLogger(__name__)
