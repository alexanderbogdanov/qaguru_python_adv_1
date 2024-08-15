from http import HTTPStatus

from fastapi import APIRouter
from app.models.AppStatus import AppStatus
from app.database import users_db


router = APIRouter()


@router.get("/api/status", response_model=AppStatus, status_code=HTTPStatus.OK)
def status() -> AppStatus:
    return AppStatus(users=bool(users_db))

