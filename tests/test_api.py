from http import HTTPStatus
import pytest
import requests
from email_validator import validate_email, EmailNotValidError
from pydantic import ValidationError
from app.models.User import User
from app.models.PaginatedResponse import PaginatedResponse


@pytest.fixture
def fill_test_data(app_url):
    pass


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
    return response.json()["items"]


class TestServiceLifeCycle:
    def test_startup(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code in [HTTPStatus.OK,
                                        HTTPStatus.NOT_FOUND], f"Expected status to be either {HTTPStatus.OK} or {HTTPStatus.NOT_FOUND}, but got {response.status_code}"


class TestUsersEndpoint:
    def test_get_all_users(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        paginated_response = response.json()
        users = paginated_response["items"]
        for user in users:
            try:
                validated_user = User(**user)
            except ValidationError as e:
                pytest.fail(f"User data validation failed for user: {user}. Error: {e}")

    def test_no_duplicate_user_ids(self, users):
        ids = [user["id"] for user in users]
        assert len(ids) == len(set(ids)), f"Duplicate user IDs found: {ids}"

    @pytest.mark.parametrize("user_id", [1, 6, 7, 12])
    def test_get_user_by_id(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for user ID {user_id}, but got {response.status_code}"

        user = response.json()
        try:
            validated_user = User(**user)
        except ValidationError as e:
            pytest.fail(f"User data validation failed for user ID {user_id}. Error: {e}")

    @pytest.mark.parametrize("user_id", [13])
    def test_user_not_found(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status {HTTPStatus.NOT_FOUND} for user ID {user_id}, but got {response.status_code}"
        assert response.json() == {
            "detail": "User not found"}, f"Expected response {{'detail': 'User not found'}}, but got {response.json()}"

    @pytest.mark.parametrize("user_id", [-1, 0])
    def test_invalid_user_id(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for invalid user ID {user_id}, but got {response.status_code}"
        assert response.json() == {
            "detail": "Invalid user ID"}, f"Expected response {{'detail': 'Invalid user ID'}}, but got {response.json()}"

    @pytest.mark.parametrize("user_id", ["a", "xyz", "!@"])
    def test_user_invalid_data_type(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for non-integer user ID {user_id}, but got {response.status_code}"
        assert response.json() == {
            "detail": [
                {
                    "type": "int_parsing",
                    "loc": ["path", "user_id"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "input": user_id,
                }
            ]
        }, f"Expected response to indicate int parsing error for user ID {user_id}, but got {response.json()}"


class TestPagination:
    def test_pagination(self, app_url):
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        paginated_response = response.json()
        assert "items" in paginated_response, "Response does not contain 'items'"
        assert len(
            paginated_response["items"]) <= 5, f"Expected up to 5 items, but got {len(paginated_response['items'])}"

    @pytest.mark.parametrize("page,size", [(1, 5), (2, 3), (3, 2)])
    def test_pagination_query_params(self, app_url, page, size):
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        paginated_response = response.json()
        assert "items" in paginated_response, "Response does not contain 'items'"
        assert len(paginated_response[
                       "items"]) <= size, f"Expected up to {size} items, but got {len(paginated_response['items'])}"

    @pytest.mark.parametrize("page,size", [(0, 5), (1, 0), (1, 101)])
    def test_pagination_invalid_params(self, app_url, page, size):
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for invalid pagination params, but got {response.status_code}"

    def test_pagination_data_differs_with_page(self, app_url):
        response_page_1 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_page_2 = requests.get(f"{app_url}/api/users/?page=2&size=5")

        assert response_page_1.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 1, but got {response_page_1.status_code}"
        assert response_page_2.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 2, but got {response_page_2.status_code}"

        data_page_1 = response_page_1.json()["items"]
        data_page_2 = response_page_2.json()["items"]

        assert data_page_1 != data_page_2, "Expected data on page 1 to differ from data on page 2"

    def test_pagination_response_model_validation(self, app_url):
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        paginated_data = response.json()
        try:
            validated_data = PaginatedResponse(**paginated_data)
        except ValidationError as e:
            pytest.fail(f"Pagination response model validation failed. Error: {e}")

    def test_pagination_out_of_bounds(self, app_url):
        response = requests.get(f"{app_url}/api/users/?page=1000&size=5")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        paginated_data = response.json()
        assert paginated_data["items"] == [], "Expected no items for out-of-bounds page, but got some items"

    def test_pagination_exceeding_page_size_limit(self, app_url):
        response = requests.get(f"{app_url}/api/users/?page=1&size=150")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for exceeding page size limit, but got {response.status_code}"

    def test_pagination_data_differs_with_size(self, app_url):
        response_size_5 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_size_10 = requests.get(f"{app_url}/api/users/?page=1&size=10")

        assert response_size_5.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page size 5, but got {response_size_5.status_code}"
        assert response_size_10.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page size 10, but got {response_size_10.status_code}"

        data_size_5 = response_size_5.json()["items"]
        data_size_10 = response_size_10.json()["items"]

        assert len(data_size_5) == 5, f"Expected 5 items for page size 5, but got {len(data_size_5)}"
        assert len(data_size_10) == 10, f"Expected 10 items for page size 10, but got {len(data_size_10)}"

    def test_pagination_total_consistency(self, app_url):
        response_page_1 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_page_2 = requests.get(f"{app_url}/api/users/?page=2&size=5")

        assert response_page_1.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 1, but got {response_page_1.status_code}"
        assert response_page_2.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 2, but got {response_page_2.status_code}"

        total_page_1 = response_page_1.json()["total"]
        total_page_2 = response_page_2.json()["total"]

        assert total_page_1 == total_page_2, f"Expected 'total' to be the same across pages, but got {total_page_1} on page 1 and {total_page_2} on page 2"

    def test_pagination_total_matches_user_count(self, app_url, users):
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        total_from_response = response.json()["total"]

        expected_total_users = 12

        assert total_from_response == expected_total_users, f"Expected 'total' to be {expected_total_users}, but got {total_from_response}"


class TestResponseValidation:
    def test_response_model(self, users):
        for user in users:
            assert isinstance(user["id"], int), f"User ID {user['id']} is not an integer"
            assert isinstance(user["email"], str), f"User email {user['email']} is not a string"
            assert isinstance(user["first_name"], str), f"User first name {user['first_name']} is not a string"
            assert isinstance(user["last_name"], str), f"User last name {user['last_name']} is not a string"
            assert isinstance(user["avatar"], str), f"User avatar URL {user['avatar']} is not a string"

    def test_response_headers(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        assert "application/json" in response.headers["Content-Type"], "Expected Content-Type to be 'application/json'"

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_response_content(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for user ID {user_id}, but got {response.status_code}"
        user = response.json()
        assert user["id"] == user_id, f"Expected user ID {user_id}, but got {user['id']}"
        assert "email" in user, "User data does not contain 'email'"
        assert "first_name" in user, "User data does not contain 'first_name'"
        assert "last_name" in user, "User data does not contain 'last_name'"
        assert "avatar" in user, "User data does not contain 'avatar'"

    def test_email_validation(self, users):
        for user in users:
            try:
                validate_email(user["email"])
            except EmailNotValidError:
                pytest.fail(f"Invalid email found: {user['email']}")

    def test_no_duplicate_emails(self, users):
        emails = [user["email"] for user in users]
        assert len(emails) == len(set(emails)), f"Duplicate emails found: {emails}"

    def test_avatar_url_validation(self, users):
        for user in users:
            try:
                validated_user = User(**user)
            except ValidationError as e:
                pytest.fail(f"Invalid avatar URL for user {user['id']}: {user['avatar']} - {e}")



