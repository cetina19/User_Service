from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy import Column, Integer, String
from infrastructure.database import Base
from sqlalchemy.orm import validates
from passlib.context import CryptContext
import jwt
import re

SECRET_KEY = "admin_key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    email = Column(String, unique=False, index=True)
    password = Column(String, unique=True, index=True)
    age = Column(Integer, index=True)

    def get_name(self):
        return self.name
    
    def get_email(self):
        return self.email
    
    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password
        self.password = pwd_context.hash(self.password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "email": self.email,
            "age": self.age
        }

    def __init__(self, name: str, email: str, password: str, age: int):
        self.name = name
        self.email = email
        self.password = password
        self.age = age
        self.validate()

    @validates('email')
    def validate_email(self, key, address):
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, address):
            raise ValueError("Invalid email address")
        return address

    @validates('age')
    def validate_age(self, key, age):
        if age < 18 or age > 100:
            raise ValueError("Age must be between 18 and 100")
        return age

    def validate(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.password or len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
class UserDelete(BaseModel):
    id: int
    name: str
    email: str
    password: str
    age: int

class UserRead(BaseModel):
    id:  Optional[int] = None
    name: str
    email: str
    password: str
    age: int

    class Config:
        orm_mode = True

    def to_dict(self):
        return {
            "name": self.name,
            "password": self.password,
            "email": self.email,
            "age": self.age
        }

class UserCreate(UserRead):
    name: str
    email: str
    password: str
    age: int

    def get_name(self):
        return self.name
    
    def get_email(self):
        return self.email
    
    def set_password(self, pwd_context: CryptContext):
        self.password = pwd_context.hash(self.password)

class UserUpdate(BaseModel):
    id:  Optional[int] = None
    name: str
    email: str
    password: str
    age: int

    def get_password(self):
        return self.password
    class Config:
        orm_mode = True

    def to_dict(self):
        return {
            "name": self.name,
            "password": self.password,
            "email": self.email,
            "age": self.age
        }
    