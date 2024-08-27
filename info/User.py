# This part of the code defines the structure (model) of user information.
from pydantic import BaseModel, EmailStr, HttpUrl  # These tools help us define and validate the structure of data.

# This class defines how a user's information should look.
class User(BaseModel):
    id: int  # Every user has a unique ID, which is a whole number.
    email: EmailStr  # Every user has an email address, which is checked to make sure it's correct.
    first_name: str  # Every user has a first name, which is a string (text).
    last_name: str  # Every user has a last name, which is a string (text).
    avatar: HttpUrl  # Every user has an avatar (profile picture), which is a URL (web address).
