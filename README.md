# FastAPI User Service

## Project Overview

The FastAPI User Service is a web service designed to manage user data. This project demonstrates building a RESTful API using FastAPI, with features such as data validation, pagination, and service status checking. Initially, the service uses a JSON file for data storage, with plans to transition to a real database and containerized deployment.

## Project Goals

1. **Implement a FastAPI Service**: Build a robust and scalable FastAPI service for managing user data.
2. **Data Validation**: Ensure all user data is validated using Pydantic models.
3. **Pagination**: Implement pagination for user data retrieval.
4. **Service Status**: Provide an endpoint to check the status of the service.
5. **Testing**: Write comprehensive tests for the API endpoints using pytest.
6. **Containerization**: Containerize the application using Docker.
7. **Database Integration**: Transition from using a JSON file to a real database like PostgreSQL.

## Features

- **User Management**: Create, read, update, and delete user data.
- **Data Validation**: Ensure user data integrity with Pydantic models.
- **Pagination**: Efficiently handle large datasets with pagination.
- **Service Status Endpoint**: Check the service status via a dedicated endpoint.
- **Comprehensive Testing**: Ensure service reliability with extensive tests.

## Project Structure

```plaintext
qaguru_python_adv_1/
├── models/
│   ├── User.py
│   └── AppStatus.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_smoke.py
├── users.json
├── .env
├── main.py
├── pyproject.toml
└── README.md
