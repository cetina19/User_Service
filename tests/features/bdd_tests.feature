Feature: Delete user
  Scenario: Delete a registered user
    Given a registered user with id "1"
    When I send a DELETE request to "/users/1"
    Then the user with id "1" should no longer exist
