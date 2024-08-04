Feature: User registration and retrieval

  Scenario: Register a new user and retrieve the user data
    When I register new user with name=alper1234, password=alper1234, email=alper8540@gmail.com, age=45
    Then the response status code should be 200
    And the response should contain the user data
    And I can check it via users endpoint
