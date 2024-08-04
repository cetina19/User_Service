FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry

RUN poetry update package

RUN poetry install --only main

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "adapters.main:app", "--host", "0.0.0.0", "--port", "8000"]
