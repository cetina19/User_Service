from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

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

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

app.include_router(router)

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

scenarios('features/bdd_tests.feature')

@given(parsers.cfparse('a registered user with id "{user_id:d}"'), target_fixture="user_id")
def create_user(db_session, user_id: int):
    user = User(id=user_id, name="Test User", email="test@example.com", password="password", age=45)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user_id

@when(parsers.cfparse('I send a DELETE request to "/users/{user_id:d}"'))
def send_delete_request(test_client: TestClient, user_id: int):
    response = test_client.delete(f"/users/{user_id}")
    assert response.status_code == 200

@then(parsers.cfparse('the user with id "{user_id:d}" should no longer exist'))
def check_user_deleted(db_session, user_id: int):
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user is None

if __name__ == "__main__":
    pytest.main()
