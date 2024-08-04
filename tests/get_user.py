import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenarios, given, when, then
from rest_api.main import app, UserDB
from ..rest_api.models.users import User
from ..rest_api import get_db

scenarios('tests/get_user.feature')

class MockDB(get_db()):
    def __init__(self):
        super().__init__()
        self.users = []

@pytest.fixture
def client():
    app.dependency_overrides[get_db()] = lambda: MockDB()
    return TestClient(app)

@given('the user with email "alper8540@gmail.com" exists')
def user_exists(client):
    user_data = {
        "email": "alper8540@gmail.com",
        "password": "password123",
        "age": 30
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

@when('I request the user with email "alper8540@gmail.com"')
def request_user(client):
    response = client.get("/users?email=alper8540@gmail.com")
    pytest.response = response

@then('the response status code should be 200')
def check_status_code():
    assert pytest.response.status_code == 200

@then('the response should contain the user data')
def check_user_data():
    response_json = pytest.response.json()
    assert response_json['email'] == "alper8540@gmail.com"
    assert 'password' not in response_json
