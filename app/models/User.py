from pydantic import EmailStr, BaseModel, HttpUrl
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    first_name: str
    last_name: str
    avatar: str  # will change later to HttpUrl


class UserCreate(BaseModel):  # let's see if it works with SQLModel
    mail: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl


class UserUpdate(BaseModel):  # let's see if it works with SQLModel
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: HttpUrl | None = None
