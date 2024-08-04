import pytest
from pytest_bdd import scenarios, given, when, then
from rest_api.services.email import EmailService
from rest_api.services.smtp import EmailService, get_email_service

# Reference the correct feature file
scenarios('features/registration.feature')

@given('the user provides valid registration details')
def user_provides_valid_details():
    # Setup for valid user details
    pass

@when('the user submits the registration form')
def user_submits_registration_form():
    # Logic to submit the registration form
    pass

@then('the user should be registered successfully')
def user_registered_successfully():
    # Assertions for successful registration
    pass
