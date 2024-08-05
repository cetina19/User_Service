Feature: Register and manage user
  Scenario: Register and update a user
    Given the following user data: "Test User", "test@example.com", "password123", 30
    When I send a POST request to "/register" with the given data
    Then the user "Test User" should be registered successfully
    When I send a PUT request to "/users/{user_id}" to update age to 50
    Then the user age should be updated to 50
