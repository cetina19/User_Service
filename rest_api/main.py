from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from typing import Any
import subprocess
from .database import SessionLocal, database, get_db
from .models.users import User, UserCreate, UserDelete, UserRead, UserUpdate
from .models.token import Auth, Token, TokenData, validate_user
from .models.responses import Responses
from .services.users import get_user, get_user_list, delete_user, put_user, add_user
from .services.smtp import get_email_service
from .services.email import EmailService
import logging

from typing import List, Optional
from dataclasses import dataclass, field


app = FastAPI()

app.mount("/static", StaticFiles(directory="rest_api/static"), name="static")
templates = Jinja2Templates(directory="rest_api/templates")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000/users",
    "http://localhost:8000/register",
    "http://localhost:8000/getToken"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="getToken")


@dataclass
class User:
    email: str
    password: str
    age: int

@dataclass
class UserDB:
    users: List[User] = field(default_factory=list)

    def add_user(self, user: User):
        self.users.append(user)

    def get_user(self, email: str) -> Optional[User]:
        for user in self.users:
            if user.email == email:
                return user
        return None

def get_db():
    return UserDB()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/register")
async def register_page():
    return {"message": "Get Page"}

@app.post("/register", response_model=Responses)
async def register_user(user: UserCreate, current_user: dict = Depends(validate_user), db: Session = Depends(get_db), email_service: EmailService = Depends(get_email_service)):
    try:
        #hashed_pwd = user.password #pwd_context.hash(user.password)
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("Email already exists")

        result = add_user(user,db)
        if result is not None:
            if isinstance(result.orig, UniqueViolation):
                result = str(result.orig).split("\nDETAIL:  ")[1].split("\n")[0] if "DETAIL" in str(result.orig) else "Duplicate entry"
            return Responses.registration_error(status_code=400,error=result)


        await email_service.send_email(
            recipient=user.email,
            subject="Welcome!",
            body=f"Hello {user.name}, thank you for registering to my server."
        )
        
        return Responses.registration_success(status_code=200, user=user)
    except ValueError as ve:
        return Responses.registration_validation_error(status_code=400,error=str(ve),user=user)  #HTTPException(status_code=400, detail=str(e))
    
    except IntegrityError as ie:
        error_message = str(ie)
        if isinstance(ie.orig, UniqueViolation):
            error_message =str(ie.orig).split("\nDETAIL:  ")[1].split("\n")[0] if "DETAIL" in str(ie.orig) else "Duplicate entry"
        return Responses.registration_error(status_code=400,error=error_message)
    
    

@app.get("/users")
async def get_users(request: Request, current_user: dict = Depends(validate_user), db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        user_list = get_user_list(users) #[{"id": user.id, "name": user.name, "email": user.email, "age": user.age} for user in users]
        return Responses.success_message(200,"Get","Got User List",user_list)
        #templates.TemplateResponse("users.html", {"request": request, "users": users})
    
    except Exception as ve:
        raise Responses.error_message(400,"Get","Couldn't Get User List",str(ve),None) #.get_users_error(400,str(ve))
    

@app.get("/users/{user_id}", response_model=UserRead)
async def api_get_user(user_id: int, current_user: dict = Depends(validate_user), db: Session = Depends(get_db)):
    user = get_user(user_id,db)
    if user is None:
        return Responses.error_message(400,"Get","Couldn't Read User","User Not Found",None) #.get_user_error(400,"User Not Found",user_id)
    return Responses.success_message(200,"Get","Got User",user.to_dict()) #.get_user_succeded(200,user.to_dict())

@app.delete("/users/{user_id}", response_model=UserDelete)
async def api_get_user(user_id: int, current_user: dict = Depends(validate_user), db: Session = Depends(get_db)):
    user = get_user(user_id,db)
    if user:
        try:
            user_response = user.to_dict()
            delete_user(user,db)
            return Responses.success_message(200,"Deletion","User Deleted", user_response) #JSONResponse({"operation": "Success", "user": user_response})
        except Exception as ve:
            return Responses.error_message(400,"Deletion","User Is Not Deleted",str(ve),user.to_dict()) #HTTPException(status_code=400, detail=str(ve))
    return Responses.error_message(400,"Deletion","User Is Not Deleted","User Not Found",None) #HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=UserUpdate)
async def update_user_age(user_id: int, user_update: UserUpdate, current_user: dict = Depends(validate_user), db: Session = Depends(get_db)):
    user = get_user(user_id, db) 
    if user:
        try:
            adding_id = {"id": user_id}
            adding_id.update(UserUpdate.from_orm(user).to_dict())
            info = {"older_info": adding_id}
            
            result = put_user(user,user_update,db)
            if result is not None:
                return Responses.error_message(400,"Update","User Is Not Updated",str(result),user.to_dict())

                            
            info["newer_info"] = user.to_dict()
            if info["newer_info"] == info["older_info"]:
                return Responses.error_message(400,"Update","User Is Not Updated","Same Credentials",user.to_dict())
            #if info["newer_info"] == info["older_info"]:
                #return Responses.error_message(400,"Update","User Is Not Updated","Same Credentials",user.to_dict())
                 #ValueError("User Is Not Updated: Same Credentials")
            db.commit()
            db.refresh(user)
            return Responses.success_message(200, "Update","User Updated", info)
        
        except ValueError as ve:
            return Responses.error_message(400,"Update","User Is Not Updated",str(ve),user.to_dict())
        
        except IntegrityError as ie:
            return Responses.error_message(400,"Update","User Is Not Updated",str(ie),user.to_dict())
    return Responses.error_message(400,"Update","User Is Not Updated","User Is Not Found",None)


@app.post("/getToken")
async def get_token(auth: Auth):
    try:
        token = Token.generate_token({"name": auth.get_name()})
        return {"token": token}
    except ValueError as e:
        return Responses.error_message(400,"Auth","Not Authenticated",str(e),None) 


@app.post("/run-tests")
async def run_tests():
    try:
        result = subprocess.run(
            ["pytest", "tests/get_user.py"], 
            capture_output=True, 
            text=True
        )
        return JSONResponse(
            content={
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            },
            status_code=200 if result.returncode == 0 else 400
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







#query = users.select()
    #result = await database.fetch_all(query)
    #return templates.TemplateResponse("users.html", {"request": request, "users": result})
    #return {"message": "Get Users"}

'''UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            age=user.age
        )'''
#user.to_dict()


"""
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        if username == "admin" and password == "admin":
            return RedirectResponse(url="/users", status_code=303)
        else:
            return JSONResponse(content={"error": "Invalid username or password"}, status_code=400) #templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
"""