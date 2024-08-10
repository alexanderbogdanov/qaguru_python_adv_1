from http import HTTPStatus
import requests


def fetch_response(url, expected_status=HTTPStatus.OK):
    response = requests.get(url)
    assert response.status_code == expected_status, f"Failed to fetch data from {url}. Expected status {expected_status}, got {response.status_code}"
    return response
