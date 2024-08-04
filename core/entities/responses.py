from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy import Column, Integer, String
from infrastructure.database import Base
from sqlalchemy.orm import validates
import re

class Responses(BaseModel):
    
    def __init__(self, error, status_code):
        self.status_code = status_code
        self.content = {
            "operation": "Catched an Exception.",
            "message": "User Registration Failed",
            "error": error,
            "user": None
        }
    
    def _build_content(self):
        return {
            "operation": self._operation,
            "message": self._message,
            "error": self._error,
            "user": self._user
        }
    
    def to_json_response(self):
        return JSONResponse(status_code=self._status_code, content=self._build_content())
    
    
    def success_message(status_code: int,operation: str, message: str, user: Any):
        return JSONResponse(
            status_code=status_code,
            content={
                "operation": operation,
                "message": message,
                "error": None,
                "user": user
            }
        )
    
    def error_message(status_code: int, operation: str, message: str, error: str, user: Any):
        return JSONResponse(
            status_code=status_code,
            content={
                "operation": operation,
                "message": message,
                "error": error,
                "user": user
            }
        )

    def registration_success(status_code: int, user: Any) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "operation": "Registration is Successful.",
                "message": "User Registered Successfully",
                "error": None,
                "user": user.to_dict()
            }
        )

    def registration_error(status_code: int, error: str):
        return JSONResponse(
            status_code=status_code,
            content={
                "operation": "Catched an Exception.",
                "message": "User Registration Failed",
                "error": error,
                "user": None
            }
        )

    def registration_validation_error(status_code: int, error: str, user: Any):
        return JSONResponse(
            status_code=status_code,
            content={
                "operation": "Validation Failed Check The Constraints.",
                "message": "User Registration Failed",
                "error": error,
                "user": user.to_dict()
            }
        )
