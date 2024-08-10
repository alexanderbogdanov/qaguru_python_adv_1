from http import HTTPStatus
import pytest
import requests
from email_validator import validate_email, EmailNotValidError
from pydantic import HttpUrl, ValidationError
from models.User import User
from models.PaginatedResponse import PaginatedResponse
from tests.utils.utils import fetch_response


@pytest.fixture
def users(app_url):
    response = fetch_response(f"{app_url}/api/users/")
    return response.json()["items"]


class TestServiceLifeCycle:
    def test_startup(self, app_url):
        response = fetch_response(f"{app_url}/api/users/")
        assert response is not None, "Service is not responding as expected"


class TestUsersEndpoint:
    def test_get_all_users(self, app_url):
        response = fetch_response(f"{app_url}/api/users/")
        users = response.json()["items"]
        for user in users:
            User.model_validate(user)

    def test_no_duplicate_user_ids(self, users):
        ids = [user["id"] for user in users]
        assert len(ids) == len(set(ids)), "Duplicate user IDs found"

    @pytest.mark.parametrize("user_id", [1, 6, 7, 12])
    def test_get_user_by_id(self, app_url, user_id):
        response = fetch_response(f"{app_url}/api/users/{user_id}")
        User.model_validate(response.json())

    @pytest.mark.parametrize("user_id", [13])
    def test_user_not_found(self, app_url, user_id):
        response = fetch_response(f"{app_url}/api/users/{user_id}", expected_status=HTTPStatus.NOT_FOUND)
        assert response.json() == {"detail": "User not found"}

    @pytest.mark.parametrize("user_id", [-1, 0])
    def test_invalid_user_id(self, app_url, user_id):
        response = fetch_response(f"{app_url}/api/users/{user_id}", expected_status=HTTPStatus.UNPROCESSABLE_ENTITY)
        assert response.json() == {"detail": "Invalid user ID"}

    @pytest.mark.parametrize("user_id", ["a", "xyz", "!@"])
    def test_user_invalid_data_type(self, app_url, user_id):
        response = fetch_response(f"{app_url}/api/users/{user_id}", expected_status=HTTPStatus.UNPROCESSABLE_ENTITY)
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
        response = fetch_response(f"{app_url}/api/users/?page=1&size=5")
        paginated_response = response.json()
        assert "items" in paginated_response, "Paginated response missing 'items'"
        assert len(paginated_response["items"]) <= 5, "Page size exceeds expected limit"

    @pytest.mark.parametrize("page,size", [(1, 5), (2, 3), (3, 2)])
    def test_pagination_query_params(self, app_url, page, size):
        response = fetch_response(f"{app_url}/api/users/?page={page}&size={size}")
        paginated_response = response.json()
        assert "items" in paginated_response, "Paginated response missing 'items'"
        assert len(
            paginated_response["items"]) <= size, f"Expected {size} items, got {len(paginated_response['items'])}"

    @pytest.mark.parametrize("page,size", [(0, 5), (1, 0), (1, 101)])
    def test_pagination_invalid_params(self, app_url, page, size):
        fetch_response(f"{app_url}/api/users/?page={page}&size={size}", expected_status=HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_pagination_data_differs_with_page(self, app_url):
        data_page_1 = fetch_response(f"{app_url}/api/users/?page=1&size=5").json()["items"]
        data_page_2 = fetch_response(f"{app_url}/api/users/?page=2&size=5").json()["items"]

        assert data_page_1 != data_page_2, "Data on page 1 should differ from data on page 2"

    def test_pagination_response_model_validation(self, app_url):
        paginated_data = fetch_response(f"{app_url}/api/users/?page=1&size=5").json()
        validated_data = PaginatedResponse(**paginated_data)

        for user in validated_data.items:
            User.model_validate(user)

    def test_pagination_out_of_bounds(self, app_url):
        paginated_data = fetch_response(f"{app_url}/api/users/?page=1000&size=5").json()
        assert paginated_data["items"] == [], "Expected empty items for out-of-bounds page"

    def test_pagination_exceeding_page_size_limit(self, app_url):
        fetch_response(f"{app_url}/api/users/?page=1&size=150", expected_status=HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_pagination_data_differs_with_size(self, app_url):
        data_size_5 = fetch_response(f"{app_url}/api/users/?page=1&size=5").json()["items"]
        data_size_10 = fetch_response(f"{app_url}/api/users/?page=1&size=10").json()["items"]

        assert len(data_size_5) == 5, "Expected 5 items on page size 5"
        assert len(data_size_10) == 10, "Expected 10 items on page size 10"


class TestResponseValidation:
    def test_response_model(self, users):
        for user in users:
            assert isinstance(user["id"], int), f"User ID is not an integer: {user['id']}"
            assert isinstance(user["email"], str), f"User email is not a string: {user['email']}"
            assert isinstance(user["first_name"], str), f"User first name is not a string: {user['first_name']}"
            assert isinstance(user["last_name"], str), f"User last name is not a string: {user['last_name']}"
            assert isinstance(user["avatar"], str), f"User avatar is not a string: {user['avatar']}"

    def test_response_headers(self, app_url):
        response = fetch_response(f"{app_url}/api/users/")
        assert "application/json" in response.headers["Content-Type"], "Content-Type header is not 'application/json'"

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_response_content(self, app_url, user_id):
        response = fetch_response(f"{app_url}/api/users/{user_id}")
        user = response.json()
        assert user["id"] == user_id, f"Expected user ID {user_id}, got {user['id']}"
        assert "email" in user, "Missing email field in user data"
        assert "first_name" in user, "Missing first_name field in user data"
        assert "last_name" in user, "Missing last_name field in user data"
        assert "avatar" in user, "Missing avatar field in user data"

    def test_email_validation(self, users):
        for user in users:
            try:
                validate_email(user["email"])
            except EmailNotValidError:
                pytest.fail(f"Invalid email: {user['email']}")

    def test_no_duplicate_emails(self, users):
        emails = [user["email"] for user in users]
        assert len(emails) == len(set(emails)), "Duplicate emails found"

    def test_avatar_url_validation(self, users):
        for user in users:
            try:
                User.model_validate(user)
            except ValidationError as e:
                pytest.fail(f"Invalid avatar URL: {user['avatar']} - {e}")
