# This part of the code defines the structure (model) for showing if the service is working correctly.
from pydantic import BaseModel  # This tool helps us define and validate the structure of data.

# This class defines how the service status should look.
class AppStatus(BaseModel):
    users: bool  # The service will tell us if the user list is loaded (True) or not (False).
