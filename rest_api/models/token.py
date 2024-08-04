import jwt
from pydantic import BaseModel, validator
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

SECRET_KEY = "admin_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/getToken")

class Token:
    @staticmethod
    def generate_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return decoded_token
        except JWTError:
            return None
        
class TokenData(BaseModel):
    token: str

class Auth(BaseModel):
    name: str
    password: str

    def get_name(self):
        return self.name
    
    def set(self, name, password):
        self.name = name
        self.password = password

    @validator('name', 'password')
    def validate_fields(cls, value, field):
        if not value:
            raise ValueError(f"{field.name.capitalize()} cannot be empty")
        if field.name == 'name' and value != 'admin':
            raise ValueError("Name or Password is not valid")
        if field.name == 'password' and value != 'admin':
            raise ValueError("Name or Password is not valid")
        return value
   
def validate_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    decoded_token = Token.verify_token(token)
    if decoded_token is None:
        raise credentials_exception
    return decoded_token
