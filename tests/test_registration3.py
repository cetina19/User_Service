import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import MagicMock
from .config import mock_db
from rest_api.main import register_user

scenarios('features/register_user.feature')

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    return 

@given('a database that does not have the user "new_user"')
def database_without_user(mock_db):
    mock_db.user_exists.return_value = False

@given('a database that already has the user "existing_user"')
def database_with_user(mock_db):
    mock_db.user_exists.return_value = True

@when('the user "new_user" registers with password "password123"')
def register_new_user(user_service):
    user_service.register_user("new_user", "password123")

@when('the user "existing_user" registers with password "password123"')
def register_existing_user(user_service):
    user_service.register_user("existing_user", "password123")

@then('the registration should be successful')
def registration_successful(user_service, mock_db):
    assert user_service.register_user("new_user", "password123") == {"status": "success", "message": "User registered successfully"}
    mock_db.add_user.assert_called_once_with("new_user", "password123")

@then('the registration should fail')
def registration_fail(user_service):
    assert user_service.register_user("existing_user", "password123") == {"status": "fail", "message": "User already exists"}
