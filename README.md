# For Build
### docker-compose build
# And then for run
### docker-compose up -d
# It runs at
### localhost:8000
<br />
Note: Passwords are hashed. <br />
Note: You need to post localhost:8000/getToken endpoint with name: "admin", password: "admin" for getting the token. It is a bearer token for operations. <br />
Note: Bdd tests are with mock database but other 2 tests are with actual database.