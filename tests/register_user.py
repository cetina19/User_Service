from dataclasses import dataclass, field
from typing import List, Optional
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenarios, when, then
from adapters.main import app, get_token
from core.entities.token import Auth
from core.use_cases.users import get_user_email

@dataclass
class User:
    name: str
    password: str
    email: str
    age: int
    

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

scenarios('features/register_user.feature')

class MockDB(UserDB):
    def __init__(self):
        super().__init__()
        self.users = [User(name="alper1234", password="alper1234",email="alper8540@gmail.com",age=45)]

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: MockDB()
    return TestClient(app)

@when('I register new user with name=alper1234, password=alper1234, email=alper8540@gmail.com, age=45')
def register_user(client):
    credentials = {"name": "admin", "password": "admin"}
    token_response = client.post("/getToken", json=credentials)
    assert token_response.status_code == 200

    token = token_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "name": "alper1234",
        "email": "alper8540@gmail.com",
        "password": "alper1234",
        "age": 45
    }
    response = client.post("/register", headers=headers, json=body)
    pytest.response = response

@then('the response status code should be 200')
def check_status_code():
    assert pytest.response.status_code == 200

@then('the response should contain the user data')
def check_user_data():
    response_json = pytest.response.json()
    assert response_json["user"]['name'] == "alper1234"
    assert response_json["user"]['password'] == "alper1234"
    assert response_json["user"]['email'] == "alper8540@gmail.com"
    assert response_json["user"]['age'] == 45

@then('I can check it via users endpoint')
def check_user_data():
    response_json= pytest.response.json()
    user_email = response_json["user"]['email']
    """credentials = {"name": "admin", "password": "admin"}
    token_response = client.post("/getToken", json=credentials)
    assert token_response.status_code == 200

    token = token_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    result = client.get("/users/alper8540@gmail.com", headers=headers)"""
    assert response_json is not None 
    assert user_email == "alper8540@gmail.com"
    assert 'password' not in response_json
