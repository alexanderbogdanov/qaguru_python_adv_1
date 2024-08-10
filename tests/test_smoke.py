from http import HTTPStatus
import requests
import socket
import os
from tests.utils.utils import fetch_response


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class TestServiceStatus:

    def test_port_in_use(self):
        port = int(os.getenv("APP_URL").split(":")[-1])
        assert is_port_in_use(port), f"Port {port} is not in use"

    def test_status_endpoint(self, app_url):
        response  = fetch_response(f"{app_url}/api/status")
        status = response.json()
        assert "users" in status, "'users' key not found in status response"
        assert isinstance(status["users"], bool), "Expected 'users' to be a boolean value"

    def test_users_endpoint(self, app_url):
        fetch_response(f"{app_url}/api/users")

    def test_get_specific_user(self, app_url):
        response = fetch_response(f"{app_url}/api/users/1")
        assert response.status_code in [HTTPStatus.OK,
                                        HTTPStatus.NOT_FOUND], "Unexpected status code when fetching user by ID"

    def test_get_user_not_found(self, app_url):
        fetch_response(f"{app_url}/api/users/999", expected_status=HTTPStatus.NOT_FOUND)
