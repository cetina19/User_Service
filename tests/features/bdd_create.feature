Feature: Register user
  Scenario: Register a new user
    Given the following user data: "Test User", "test@example.com", "password123", 30
    When I send a POST request to "/register" with the given data
    Then the user "Test User" should be registered successfully
