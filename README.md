poetry init --name rest_api --dependency fastapi --dependency uvicorn --dependency sqlalchemy --dependency psycopg2-binary --no-interaction

poetry add fastapi uvicorn sqlalchemy psycopg2-binary databases

poetry update package

# docker-compose build
and then
# docker-compose up -d
It runs at
# localhost:8000