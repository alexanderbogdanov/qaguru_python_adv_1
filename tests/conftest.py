import os
from http import HTTPStatus

import dotenv
import pytest
import requests


@pytest.fixture(autouse=True, scope="session")
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


def fetch_response(url, expected_status=HTTPStatus.OK):
    response = requests.get(url)
    assert response.status_code == expected_status, f"Failed to fetch data from {url}. Expected status {expected_status}, got {response.status_code}"
    return response.json() if response.status_code == HTTPStatus.OK else response
