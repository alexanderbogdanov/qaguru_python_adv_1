from http import HTTPStatus
import socket
import os

import pytest
import requests
from app.models.AppStatus import AppStatus
from app.models.User import User
from pydantic import ValidationError


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class TestServiceStatus:
    def test_port_in_use(self):
        port = int(os.getenv("APP_URL").split(":")[-1])
        assert is_port_in_use(port), f"Port {port} is not in use"

    def test_status_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/status")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for status endpoint, but got {response.status_code}"
        status = response.json()
        try:
            AppStatus(**status)
        except ValidationError as e:
            pytest.fail(f"Status endpoint response validation failed. Error: {e}")

    def test_users_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for users endpoint, but got {response.status_code}"

    def test_get_specific_user(self, app_url):
        response = requests.get(f"{app_url}/api/users/1")
        assert response.status_code in [HTTPStatus.OK,
                                        HTTPStatus.NOT_FOUND], f"Expected status to be either {HTTPStatus.OK} or {HTTPStatus.NOT_FOUND}, but got {response.status_code}"

        if response.status_code == HTTPStatus.OK:
            try:
                validated_user = User(**response.json())
            except ValidationError as e:
                pytest.fail(f"Validation failed for user data: {e}")

    def test_get_user_not_found(self, app_url):
        response = requests.get(f"{app_url}/api/users/999")
        assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status {HTTPStatus.NOT_FOUND} for non-existent user, but got {response.status_code}"
        assert response.json() == {
            "detail": "User not found"}, f"Expected response {{'detail': 'User not found'}}, but got {response.json()}"



