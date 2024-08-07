from http import HTTPStatus
import pytest
import requests
from email_validator import validate_email, EmailNotValidError
from pydantic import HttpUrl, ValidationError
from models.User import User


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


class TestServiceLifeCycle:
    def test_startup(self, app_url):
        response = requests.get(app_url)
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]


class TestUsersEndpoint:
    def test_get_all_users(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK

        paginated_response = response.json()
        users = paginated_response["items"]
        for user in users:
            User.model_validate(user)

    def test_no_duplicate_user_ids(self, users):
        items = users["items"]
        ids = [user["id"] for user in items]
        assert len(ids) == len(set(ids)), "Duplicate user IDs found"

    @pytest.mark.parametrize("user_id", [1, 6, 7, 12])
    def test_get_user_by_id(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK

        user = response.json()
        User.model_validate(user)

    @pytest.mark.parametrize("user_id", [13])
    def test_user_not_found(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {"detail": "User not found"}

    @pytest.mark.parametrize("user_id", [-1, 0])
    def test_invalid_user_id(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {"detail": "Invalid user ID"}

    @pytest.mark.parametrize("user_id", ["a", "xyz", "!@"])
    def test_user_invalid_data_type(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "type": "int_parsing",
                    "loc": ["path", "user_id"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "input": user_id,
                }
            ]
        }


class TestPagination:
    def test_pagination(self, app_url):
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        assert response.status_code == HTTPStatus.OK
        paginated_response = response.json()
        assert "items" in paginated_response
        assert len(paginated_response["items"]) <= 5

    @pytest.mark.parametrize("page,size", [(1, 5), (2, 3), (3, 2)])
    def test_pagination_query_params(self, app_url, page, size):
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.OK
        paginated_response = response.json()
        assert "items" in paginated_response
        assert len(paginated_response["items"]) <= size

    @pytest.mark.parametrize("page,size", [(0, 5), (1, 0), (1, 101)])
    def test_pagination_invalid_params(self, app_url, page, size):
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

class TestResponseValidation:
    def test_response_model(self, users):
        items = users["items"]
        for user in items:
            assert isinstance(user["id"], int)
            assert isinstance(user["email"], str)
            assert isinstance(user["first_name"], str)
            assert isinstance(user["last_name"], str)
            assert isinstance(user["avatar"], str)

    def test_response_headers(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK
        assert "application/json" in response.headers["Content-Type"]

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_response_content(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        assert user["id"] == user_id
        assert "email" in user
        assert "first_name" in user
        assert "last_name" in user
        assert "avatar" in user

    def test_email_validation(self, users):
        items = users["items"]
        for user in items:
            try:
                validate_email(user["email"])
            except EmailNotValidError:
                pytest.fail(f"Invalid email: {user['email']}")

    def test_no_duplicate_emails(self, users):
        items = users["items"]
        emails = [user["email"] for user in items]
        assert len(emails) == len(set(emails)), "Duplicate emails found"

    def test_avatar_url_validation(self, users):
        items = users["items"]
        for user in items:
            try:
                User.model_validate(user)
            except ValidationError as e:
                pytest.fail(f"Invalid avatar URL: {user['avatar']} - {e}")

