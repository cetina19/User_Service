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

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email, password=user.password, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "name": db_user.name, "email": db_user.email, "age": db_user.age}

@router.get("/user", response_model=UserResponse)
def get_user(user_id: int = None, email: str = None, db: Session = Depends(get_db)):
    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
    elif email is not None:
        user = db.query(User).filter(User.email == email).first()
    else:
        raise HTTPException(status_code=400, detail="Must provide either user_id or email")
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "name": user.name, "email": user.email, "age": user.age}

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

scenarios('features/bdd_get.feature')

@given(parsers.cfparse('the following user data: "{name}", "{email}", "{password}", {age:d}'), target_fixture="user_data")
def user_data(name: str, email: str, password: str, age: int):
    return {"name": name, "email": email, "password": password, "age": age}

@when('I send a POST request to "/register" with the given data')
def send_post_request(test_client: TestClient, user_data: dict):
    response = test_client.post("/register", json=user_data)
    assert response.status_code == 200
    pytest.user_id = response.json()["id"]
    pytest.user_email = response.json()["email"]

@then('the user "Test User" should be registered successfully')
def check_user_registered(db_session, user_data: dict):
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.age == user_data["age"]

@when('I send a GET request to "/user" with user_id')
def send_get_request_by_id(test_client: TestClient):
    response = test_client.get(f"/user?user_id={pytest.user_id}")
    assert response.status_code == 200
    pytest.user_response = response.json()

@when('I send a GET request to "/user" with email')
def send_get_request_by_email(test_client: TestClient):
    response = test_client.get(f"/user?email={pytest.user_email}")
    assert response.status_code == 200
    pytest.user_response = response.json()

@then('I should get the correct user data')
def check_get_user_response():
    assert pytest.user_response["id"] == pytest.user_id
    assert pytest.user_response["name"] == "Test User"
    assert pytest.user_response["email"] == "test@example.com"
    assert pytest.user_response["age"] == 30

if __name__ == "__main__":
    pytest.main()
