import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import MagicMock
from ..rest_api.main import register_user  
from sqlalchemy.orm import Session
from fastapi import Depends
from ..rest_api.models.users import UserCreate  
from ..rest_api.services.email import EmailService, get_email_service  
from ..rest_api.database import get_db  

# Load the scenarios from the feature file
scenarios('features/registration.feature')

@pytest.fixture
def user_data():
    return {'name': 'testuser', 'email': 'alper8540@gmail.com', 'password': 'securepassword', 'age': 25}

@given('a user with email "<email>" and password "<password>"')
def user(user_data, email, password):
    user_data['email'] = email
    user_data['password'] = password
    return user_data

@given('the email "<email>" already exists')
def email_exists(mock_db, email):
    mock_db.query.return_value.filter.return_value.first.return_value = {'email': email}

@when('the user registers')
def user_register(mock_db, user_data):
    try:
        register_user(
            user=UserCreate(**user_data),
            db=mock_db,
            email_service=MagicMock()
        )
        pytest.context['register_success'] = True
    except ValueError as e:
        pytest.context['register_success'] = False
        pytest.context['error_message'] = str(e)

@then('the user should be successfully registered')
def successful_registration(mock_db):
    assert pytest.context['register_success']
    mock_db.add.assert_called_once()

@then('the registration should fail with message "Email already exists"')
def registration_failure(mock_db):
    assert not pytest.context['register_success']
    assert pytest.context['error_message'] == "Email already exists"
    mock_db.add.assert_not_called()
