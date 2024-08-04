Feature: User Registration
  Scenario: Registering an already existing user
    Given a database that already has the user "existing_user"
    And a user with email "existing_user@example.com" and password "password123"
    When the user registers
    Then the registration should fail with message "Email already exists"
