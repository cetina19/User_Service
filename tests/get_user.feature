Feature: Get User
  As an API client
  I want to retrieve user information
  So that I can see the details of a registered user

  Scenario: Retrieve a specific user
    Given the user with email "alper8540@gmail.com" exists
    When I request the user with email "alper8540@gmail.com"
    Then the response status code should be 200
    And the response should contain the user data
