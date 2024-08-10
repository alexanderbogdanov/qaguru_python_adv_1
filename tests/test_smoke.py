from http import HTTPStatus
import requests
import socket
import os


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class TestServiceStatus:

    def test_port_in_use(self):
        port = int(os.getenv("APP_URL").split(":")[-1])
        assert is_port_in_use(port), f"Port {port} is not in use"

    def test_status_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/status")
        assert response.status_code == HTTPStatus.OK
        status = response.json()
        assert "users" in status
        assert isinstance(status["users"], bool)

    def test_users_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.OK

    def test_get_specific_user(self, app_url):
        response = requests.get(f"{app_url}/api/users/1")
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]

    def test_get_user_not_found(self, app_url):
        response = requests.get(f"{app_url}/api/users/999")
        assert response.status_code == HTTPStatus.NOT_FOUND
