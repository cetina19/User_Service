from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

from fastapi.testclient import TestClient
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
router = APIRouter()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    age = Column(Integer, index=True)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    age: int

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email, password=user.password, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email, "age": db_user.age}

app.include_router(router)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

scenarios('features/bdd_create.feature')

@given(parsers.cfparse('the following user data: "{name}", "{email}", "{password}", {age:d}'), target_fixture="user_data")
def user_data(name: str, email: str, password: str, age: int):
    return {"name": name, "email": email, "password": password, "age": age}

@when('I send a POST request to "/register" with the given data')
def send_post_request(test_client: TestClient, user_data: dict):
    response = test_client.post("/register", json=user_data)
    assert response.status_code == 200
    pytest.user_id = response.json()["id"]

@then('the user "Test User" should be registered successfully')
def check_user_registered(db_session, user_data: dict):
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.age == user_data["age"]

if __name__ == "__main__":
    pytest.main()
