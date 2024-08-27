# This part of the code is bringing in tools that help us test our web service to make sure it works correctly.
from http import HTTPStatus  # This helps us use specific numbers to represent different outcomes when people interact with our program.
import pytest  # This is a tool that helps us create and run tests automatically.
import requests  # This helps us send requests to our web service to see how it responds.
from email_validator import validate_email, EmailNotValidError  # This helps us check if email addresses are correct.
from pydantic import ValidationError  # These tools help us check if URLs (web addresses) and other data are correct.
from app.models.User import User  # This tells our tests to use the format we defined for user information.
from app.models.PaginatedResponse import PaginatedResponse  # This tells our tests to use the format we defined for paginated responses.

# This creates a fixture, which is a helper that runs before our tests to set things up.
@pytest.fixture
def users(app_url):
    # We send a request to our service to get a list of users.
    response = requests.get(f"{app_url}/api/users/")
    # We check if the response from our service is okay (status 200).
    assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
    # We return the list of users to be used in our tests.
    return response.json()["items"]

# This class contains tests that check if our service starts up correctly.
class TestServiceLifeCycle:
    def test_startup(self, app_url):
        """Test to ensure the service is running by checking a valid endpoint."""
        # We send a request to our service and check if it starts up correctly.
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND], f"Expected status to be either {HTTPStatus.OK} or {HTTPStatus.NOT_FOUND}, but got {response.status_code}"

# This class contains tests that check if the user-related features of our service work correctly.
class TestUsersEndpoint:
    def test_get_all_users(self, app_url):
        """Test to fetch all users and validate their structure."""
        # We send a request to get all users.
        response = requests.get(f"{app_url}/api/users/")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        # We get the list of users from the response.
        paginated_response = response.json()
        users = paginated_response["items"]
        # We check if each user's information is correct.
        for user in users:
            try:
                validated_user = User(**user)  # We validate each user by creating an instance of User.
            except ValidationError as e:
                pytest.fail(f"User data validation failed for user: {user}. Error: {e}")

    def test_no_duplicate_user_ids(self, users):
        """Test to ensure no duplicate user IDs exist."""
        # We check if any user IDs are repeated.
        ids = [user["id"] for user in users]
        assert len(ids) == len(set(ids)), f"Duplicate user IDs found: {ids}"

    @pytest.mark.parametrize("user_id", [1, 6, 7, 12])
    def test_get_user_by_id(self, app_url, user_id):
        """Test to fetch a user by ID and validate the response."""
        # We send a request to get a specific user by ID.
        response = requests.get(f"{app_url}/api/users/{user_id}")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for user ID {user_id}, but got {response.status_code}"

        # We check if the user's information is correct.
        user = response.json()
        try:
            validated_user = User(**user)  # We validate the user by creating an instance of User.
        except ValidationError as e:
            pytest.fail(f"User data validation failed for user ID {user_id}. Error: {e}")

    @pytest.mark.parametrize("user_id", [13])
    def test_user_not_found(self, app_url, user_id):
        """Test to ensure the API returns a 404 status for non-existent users."""
        # We send a request for a user that doesn't exist.
        response = requests.get(f"{app_url}/api/users/{user_id}")
        # We check if the response is "User not found" (status 404).
        assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status {HTTPStatus.NOT_FOUND} for user ID {user_id}, but got {response.status_code}"
        assert response.json() == {"detail": "User not found"}, f"Expected response {{'detail': 'User not found'}}, but got {response.json()}"

    @pytest.mark.parametrize("user_id", [-1, 0])
    def test_invalid_user_id(self, app_url, user_id):
        """Test to ensure the API returns a 422 status for invalid user IDs."""
        # We send a request with an invalid user ID.
        response = requests.get(f"{app_url}/api/users/{user_id}")
        # We check if the response is "Invalid user ID" (status 422).
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for invalid user ID {user_id}, but got {response.status_code}"
        assert response.json() == {"detail": "Invalid user ID"}, f"Expected response {{'detail': 'Invalid user ID'}}, but got {response.json()}"

    @pytest.mark.parametrize("user_id", ["a", "xyz", "!@"])
    def test_user_invalid_data_type(self, app_url, user_id):
        """Test to ensure the API returns a 422 status for non-integer user IDs."""
        # We send a request with a user ID that's not a number.
        response = requests.get(f"{app_url}/api/users/{user_id}")
        # We check if the response is "Invalid input" (status 422).
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

# This class contains tests that check if the pagination (showing information in pieces) works correctly.
class TestPagination:
    def test_pagination(self, app_url):
        """Test basic pagination functionality."""
        # We send a request to get the first page of users with a size of 5.
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        paginated_response = response.json()
        # We check if there are up to 5 users on the page.
        assert "items" in paginated_response, "Response does not contain 'items'"
        assert len(paginated_response["items"]) <= 5, f"Expected up to 5 items, but got {len(paginated_response['items'])}"

    @pytest.mark.parametrize("page,size", [(1, 5), (2, 3), (3, 2)])
    def test_pagination_query_params(self, app_url, page, size):
        """Test different pagination query parameters."""
        # We send requests for different pages and sizes.
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        paginated_response = response.json()
        # We check if the number of users matches the requested size.
        assert "items" in paginated_response, "Response does not contain 'items'"
        assert len(paginated_response["items"]) <= size, f"Expected up to {size} items, but got {len(paginated_response['items'])}"

    @pytest.mark.parametrize("page,size", [(0, 5), (1, 0), (1, 101)])
    def test_pagination_invalid_params(self, app_url, page, size):
        """Test invalid pagination parameters."""
        # We send requests with invalid page or size values.
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")
        # We check if the response is "Unprocessable Entity" (status 422).
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for invalid pagination params, but got {response.status_code}"

    def test_pagination_data_differs_with_page(self, app_url):
        """Test that data on different pages is distinct."""
        # We send requests to get the first and second pages of users.
        response_page_1 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_page_2 = requests.get(f"{app_url}/api/users/?page=2&size=5")

        # We check if the responses are okay (status 200).
        assert response_page_1.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 1, but got {response_page_1.status_code}"
        assert response_page_2.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 2, but got {response_page_2.status_code}"

        # We check if the data on the first and second pages is different.
        data_page_1 = response_page_1.json()["items"]
        data_page_2 = response_page_2.json()["items"]
        assert data_page_1 != data_page_2, "Expected data on page 1 to differ from data on page 2"

    def test_pagination_response_model_validation(self, app_url):
        """Test that the paginated response matches the expected model."""
        # We send a request to get the first page of users with a size of 5.
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        # We validate the structure of the response against our PaginatedResponse model.
        paginated_data = response.json()
        try:
            validated_data = PaginatedResponse(**paginated_data)
        except ValidationError as e:
            pytest.fail(f"Pagination response model validation failed. Error: {e}")

    def test_pagination_total_consistency(self, app_url):
        """Test that the 'total' field is consistent across different pages."""
        # We send requests to get the first and second pages of users.
        response_page_1 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_page_2 = requests.get(f"{app_url}/api/users/?page=2&size=5")

        # We check if the responses are okay (status 200).
        assert response_page_1.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 1, but got {response_page_1.status_code}"
        assert response_page_2.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page 2, but got {response_page_2.status_code}"

        # We check if the total number of users is the same on both pages.
        total_page_1 = response_page_1.json()["total"]
        total_page_2 = response_page_2.json()["total"]
        assert total_page_1 == total_page_2, f"Expected 'total' to be the same across pages, but got {total_page_1} on page 1 and {total_page_2} on page 2"

    def test_pagination_total_matches_user_count(self, app_url):
        """Test that the 'total' field matches the actual number of users."""
        # We send a request to get the first page of users with a size of 5.
        response = requests.get(f"{app_url}/api/users/?page=1&size=5")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        # We check if the total number of users in the response matches the actual number of users.
        total_from_response = response.json()["total"]
        expected_total_users = 12  # Hardcoded value assuming 12 users in users.json
        assert total_from_response == expected_total_users, f"Expected 'total' to be {expected_total_users}, but got {total_from_response}"

    def test_pagination_out_of_bounds(self, app_url):
        """Test that an out-of-bounds page returns an empty result."""
        # We send a request to get a page that is beyond the number of users we have.
        response = requests.get(f"{app_url}/api/users/?page=1000&size=5")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"

        # We check if the items on this page are empty, as expected.
        paginated_data = response.json()
        assert paginated_data["items"] == [], "Expected no items for out-of-bounds page, but got some items"

    def test_pagination_exceeding_page_size_limit(self, app_url):
        """Test that exceeding the page size limit returns a 422 status."""
        # We send a request with a size that is too large.
        response = requests.get(f"{app_url}/api/users/?page=1&size=150")  # Assuming max allowed size is 100
        # We check if the response is "Unprocessable Entity" (status 422).
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f"Expected status {HTTPStatus.UNPROCESSABLE_ENTITY} for exceeding page size limit, but got {response.status_code}"

    def test_pagination_data_differs_with_size(self, app_url):
        """Test that changing the page size affects the number of items returned."""
        # We send requests to get the first page of users with different sizes.
        response_size_5 = requests.get(f"{app_url}/api/users/?page=1&size=5")
        response_size_10 = requests.get(f"{app_url}/api/users/?page=1&size=10")

        # We check if the responses are okay (status 200).
        assert response_size_5.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page size 5, but got {response_size_5.status_code}"
        assert response_size_10.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for page size 10, but got {response_size_10.status_code}"

        # We check if the number of items matches the requested size.
        data_size_5 = response_size_5.json()["items"]
        data_size_10 = response_size_10.json()["items"]
        assert len(data_size_5) == 5, f"Expected 5 items for page size 5, but got {len(data_size_5)}"
        assert len(data_size_10) == 10, f"Expected 10 items for page size 10, but got {len(data_size_10)}"

# This class contains tests that check if the structure and content of the responses are correct.
class TestResponseValidation:
    def test_response_model(self, users):
        """Test that each user in the response matches the expected model."""
        # We check if each user's information is correct.
        for user in users:
            assert isinstance(user["id"], int), f"User ID {user['id']} is not an integer"
            assert isinstance(user["email"], str), f"User email {user['email']} is not a string"
            assert isinstance(user["first_name"], str), f"User first name {user['first_name']} is not a string"
            assert isinstance(user["last_name"], str), f"User last name {user['last_name']} is not a string"
            assert isinstance(user["avatar"], str), f"User avatar URL {user['avatar']} is not a string"

    def test_response_headers(self, app_url):
        """Test that the API returns the correct Content-Type header."""
        # We send a request to get all users.
        response = requests.get(f"{app_url}/api/users/")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, but got {response.status_code}"
        # We check if the content type of the response is JSON.
        assert "application/json" in response.headers["Content-Type"], "Expected Content-Type to be 'application/json'"

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_response_content(self, app_url, user_id):
        """Test that the content of the response matches the expected user data."""
        # We send a request to get a specific user by ID.
        response = requests.get(f"{app_url}/api/users/{user_id}")
        # We check if the response is okay (status 200).
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for user ID {user_id}, but got {response.status_code}"
        # We check if the user's information is correct.
        user = response.json()
        assert user["id"] == user_id, f"Expected user ID {user_id}, but got {user['id']}"
        assert "email" in user, "User data does not contain 'email'"
        assert "first_name" in user, "User data does not contain 'first_name'"
        assert "last_name" in user, "User data does not contain 'last_name'"
        assert "avatar" in user, "User data does not contain 'avatar'"

    def test_email_validation(self, users):
        """Test that all user emails are valid."""
        # We check if each user's email is correct.
        for user in users:
            try:
                validate_email(user["email"])
            except EmailNotValidError:
                pytest.fail(f"Invalid email found: {user['email']}")

    def test_no_duplicate_emails(self, users):
        """Test that no duplicate emails exist in the user data."""
        # We check if any emails are repeated.
        emails = [user["email"] for user in users]
        assert len(emails) == len(set(emails)), f"Duplicate emails found: {emails}"

    def test_avatar_url_validation(self, users):
        """Test that all user avatar URLs are valid."""
        # We check if each user's avatar URL is correct.
        for user in users:
            try:
                validated_user = User(**user)  # We validate the user by creating an instance of User.
            except ValidationError as e:
                pytest.fail(f"Invalid avatar URL for user {user['id']}: {user['avatar']} - {e}")
