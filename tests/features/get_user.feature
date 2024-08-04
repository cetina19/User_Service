Feature: Retrieve a specific user

  Scenario: Retrieve a user by email
    When I request the user with email "alper8542@gmail.com"
    Then the response status code should be 200
    And the response should contain the user data
