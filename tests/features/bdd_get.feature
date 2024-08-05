Feature: Register and get user
  Scenario: Register and get the registered user
    Given the following user data: "Test User", "test@example.com", "password123", 30
    When I send a POST request to "/register" with the given data
    Then the user "Test User" should be registered successfully
    When I send a GET request to "/user" with user_id
    Then I should get the correct user data
    When I send a GET request to "/user" with email
    Then I should get the correct user data
