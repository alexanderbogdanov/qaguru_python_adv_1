from pydantic import EmailStr, BaseModel, HttpUrl
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str  # will change later to HttpUrl

class UserCreate(BaseModel):
    mail: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl



class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: HttpUrl | None = None
