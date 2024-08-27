from http import HTTPStatus

from fastapi import APIRouter

from app.database.engine import check_if_db_available
from app.models.AppStatus import AppStatus
from app.database import users

router = APIRouter()


@router.get("/api/status", response_model=AppStatus, status_code=HTTPStatus.OK)
def status() -> AppStatus:
    return AppStatus(database=check_if_db_available())

