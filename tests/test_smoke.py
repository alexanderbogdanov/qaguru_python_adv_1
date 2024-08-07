from http import HTTPStatus

import requests


class TestServiceStatus:
    def test_status_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/status")
        assert response.status_code == HTTPStatus.OK
        status = response.json()
        assert "users" in status
        assert isinstance(status["users"], bool)

    def test_users_endpoint(self, app_url):
        response = requests.get(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.OK
        users = response.json()
        assert "items" in users
        assert isinstance(users["items"], list)

    def test_get_specific_user(self, app_url):
        response = requests.get(f"{app_url}/api/users/1")
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        if response.status_code == HTTPStatus.OK:
            user = response.json()
            assert isinstance(user, dict)
            assert "id" in user
            assert "email" in user
            assert "first_name" in user
            assert "last_name" in user
            assert "avatar" in user

    def test_get_user_not_found(self, app_url):
        response = requests.get(f"{app_url}/api/users/999")
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {"detail": "User not found"}
