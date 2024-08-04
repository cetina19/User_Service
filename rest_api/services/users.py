#from requests import Session
from rest_api.models.responses import Responses
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..models.users import User, UserUpdate, UserCreate
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from fastapi import Depends
from fastapi import HTTPException

def add_user(user: UserCreate, db: Session):
    try:
        user = User(name=user.name, email=user.email, password=user.password, age=user.age)
        db.add(user)
        db.commit()
        db.refresh(user)
    except ValueError as ve:
        return ve
    except IntegrityError as ie:
        return ie
    return None

def get_user(user_id: int, db: Session):
    return db.query(User).filter(User.id == user_id).first()

def get_user_list(users):
    return [{"id": user.id, "name": user.name, "email": user.email, "age": user.age} for user in users]

def delete_user(user: User, db: Session):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

def put_user(user: User, user_update: UserUpdate, db: Session):
    try:
        if user_update.name is not None:
            user.name = user_update.name
        if user_update.password is not None:
            user.password = user_update.password
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.age is not None:
            user.age = user_update.age
        db.commit()
        db.refresh(user)
        
    except ValueError as ve:
        return ve
    except IntegrityError as ie:
        return ie 
    return None