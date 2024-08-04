from dataclasses import dataclass, field
from typing import List, Optional
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenarios, given, when, then
from rest_api.main import app

fake_users_db = {
    "alper8542@gmail.com": {
        "name": "alper6",
        "email": "alper8542@gmail.com",
        "password": "alp884e3",
        "age": 40,
    }
}

@dataclass
class User:
    email: str
    name: str

@dataclass
class UserDB:
    users: List[User] = field(default_factory=list)

    def add_user(self, user: User):
        self.users.append(user)

    def get_user(self, email: str) -> Optional[User]:
        for user in self.users:
            if user.email == email:
                return user
        return None

def get_db():
    return UserDB()


scenarios('get_user.feature')

class MockDB(UserDB):
    def __init__(self):
        super().__init__()
        self.users = []

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: MockDB()
    return TestClient(app)

@given('the user with email "alper8542@gmail.com" exists')
def user_exists(client):
    user_data = {
        "name": "alper6",
        "email": "alper8542@gmail.com",
        "password": "alperss2a3sa91",
        "age": 40
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

@when('I request the user with email "alper8542@gmail.com"')
def request_user(client):
    response = client.get("/users2/alper8542@gmail.com")
    pytest.response = response

@then('the response status code should be 200')
def check_status_code():
    assert pytest.response.status_code == 200

@then('the response should contain the user data')
def check_user_data():
    response_json = pytest.response.json()
    assert response_json['email'] == "alper8542@gmail.com"
    assert 'password' not in response_json
