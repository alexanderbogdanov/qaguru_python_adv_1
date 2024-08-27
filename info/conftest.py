# This part of the code is setting up helpers that run before our tests to set things up.
import os  # This helps us work with the operating system, like reading environment variables.
import dotenv  # This helps us load environment variables from a file.
import pytest  # This is a tool that helps us create and run tests automatically.

# This helper loads environment variables from a file before our tests run.
@pytest.fixture(autouse=True)
def envs():
    dotenv.load_dotenv()

# This helper gets the base URL for our web service from an environment variable.
@pytest.fixture
def app_url():
    return os.getenv("APP_URL")
