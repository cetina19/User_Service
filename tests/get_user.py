from dataclasses import dataclass, field
from typing import List, Optional
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenarios, when, then
from adapters.main import app, get_token
from core.entities.token import Auth

@dataclass
class User:
    name: str
    email: str

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

scenarios('features/get_user.feature')

class MockDB(UserDB):
    def __init__(self):
        super().__init__()
        self.users = [User(email="alper8542@gmail.com", name="Alper7")]

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: MockDB()
    return TestClient(app)

@when('I request the user with email "alper8542@gmail.com"')
def request_user(client):
    credentials = {"name": "admin", "password": "admin"}
    token_response = client.post("/getToken", json=credentials)
    assert token_response.status_code == 200
    token = token_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/alper8542@gmail.com", headers=headers)
    pytest.response = response

@then('the response status code should be 200')
def check_status_code():
    assert pytest.response.status_code == 200

@then('the response should contain the user data')
def check_user_data():
    response_json = pytest.response.json()
    assert response_json["user"]['email'] == "alper8542@gmail.com"
    assert 'password' not in response_json
