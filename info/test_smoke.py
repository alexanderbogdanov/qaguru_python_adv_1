# This part of the code is bringing in tools to check if our service is alive and responding correctly.
from http import HTTPStatus  # This helps us use specific numbers to represent different outcomes when people interact with our program.
import socket  # This helps us check if a specific port on our computer is being used.
import os  # This helps us work with the operating system, like reading environment variables.

import pytest
import requests  # This helps us send requests to our web service to see how it responds.
from app.models.AppStatus import AppStatus  # This tells our tests to use the format we defined for the status response.
from app.models.User import User  # This tells our tests to use the format we defined for user information.
from pydantic import ValidationError  # This helps us check if data is correct according to our model.

# This function checks if a specific port is being used.
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

# This class contains tests that check if the service is alive and responding.
class TestServiceStatus:
    def test_port_in_use(self):
        """Test to check if the service port is in use."""
        # We get the port number from the URL and check if it's in use.
        port = int(os.getenv("APP_URL").split(":")[-1])
        assert is_port_in_use(port), f"Port {port} is not in use"

    def test_status_endpoint(self, app_url):
        """Test the /api/status endpoint to ensure the service is running."""
        # We send a request to the status endpoint and check if it responds correctly.
        response = requests.get(f"{app_url}/api/status")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for status endpoint, but got {response.status_code}"
        # We check if the status response matches our model.
        status = response.json()
        try:
            AppStatus(**status)
        except ValidationError as e:
            pytest.fail(f"Status endpoint response validation failed. Error: {e}")

    def test_users_endpoint(self, app_url):
        """Test the /api/users endpoint to ensure users can be fetched."""
        # We send a request to the users endpoint and check if it responds correctly.
        response = requests.get(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK} for users endpoint, but got {response.status_code}"

    def test_get_specific_user(self, app_url):
        """Test fetching a specific user by ID."""
        # We send a request to get a specific user by ID and check if it responds correctly.
        response = requests.get(f"{app_url}/api/users/1")
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND], f"Expected status to be either {HTTPStatus.OK} or {HTTPStatus.NOT_FOUND}, but got {response.status_code}"

        # If the user exists, we validate their information.
        if response.status_code == HTTPStatus.OK:
            try:
                validated_user = User(**response.json())
            except ValidationError as e:
                pytest.fail(f"Validation failed for user data: {e}")

    def test_get_user_not_found(self, app_url):
        """Test fetching a non-existent user to ensure proper 404 response."""
        # We send a request for a user that doesn't exist and check if the response is "User not found" (status 404).
        response = requests.get(f"{app_url}/api/users/999")
        assert response.status_code == HTTPStatus.NOT_FOUND, f"Expected status {HTTPStatus.NOT_FOUND} for non-existent user, but got {response.status_code}"
        assert response.json() == {"detail": "User not found"}, f"Expected response {{'detail': 'User not found'}}, but got {response.json()}"
