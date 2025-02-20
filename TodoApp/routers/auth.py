from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException, Request
from pydantic import BaseModel
from ..models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer 
"""
# We use OAuth2PasswordRequestForm, as against a normal FastAPI form, because it's slightly more secure. It will have it's own portal on swagger where we can enter the username and password for the request.
# We use OAuth2PasswordBearer to decode a JWT. Decoding a JWT is the only way to verify that a JWT is authenticated. ... when a user logs in, we pass in the username and password, we return a JWT and each API endpoint that needs security or authorization, we are going to verify the JWT that the client is going to pass in to make sure that it's secure and hasn't been messed with. ...In the header of every API endpoint we are going to pass in this bearer token - JWT, ... & we are just telling FastAPI to check the bearer token in the header for this JWT before we process this request.
"""
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

"""
To generate a unique secret key, do this on the terminal:
`$ openssl rand -hex 32`
Copy the long text and use it as the secret key.
-> The secret key and the algorithm will work together to add a signature to the JWT to make sure the JWT is secure and authorized.
"""
SECRET_KEY = 'c1146a21a4e60e6d01eea798041269cf0ae069da619b096350470f1bf16a8690'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
"""
# This is a dependency that each API endpoint will rely on. The `tokenUrl='auth/token'` parameter contains the url that the client will send to our FastAPI application. So we need this just to verify the token as a dependency in our API request.
"""
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') 

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str 
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal() # Create a new database session
    try:
        yield db # Provide the session to the request handler
    finally:
        db.close() # Close the session after request is completed

# This line ensures that the get_db() is called whenever a route requires a database session.
db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="TodoApp/templates")

### Pages ###
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


### Endpoints ###
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

"""
# For each api call in the future that needs security, we are going to call this `get_current_user` first to verify the token that's getting passed in as the OAuth2 bearer token in a client call
"""
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
                        db: db_dependency, 
                        create_user_request: CreateUserRequest
                    ):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    # return create_user_model # use this if you want to see what create_user_model looks like.
    db.add(create_user_model)
    db.commit()
    
@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
    ): # here we are saying that this function relies on our form data which has a dependency injection of OAuth2PasswordRequestForm
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.'
        )
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    
    return {'access_token': token, 'token_type': 'bearer'}
    