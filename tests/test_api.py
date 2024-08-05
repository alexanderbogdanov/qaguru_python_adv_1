from http import HTTPStatus

import requests
from models.User import User


def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK

    paginated_response = response.json()
    users = paginated_response["items"]
    for user in users:
        User.model_validate(user)
