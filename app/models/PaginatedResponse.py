from pydantic import BaseModel
from typing import List
from app.models.User import User


class PaginatedResponse(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
