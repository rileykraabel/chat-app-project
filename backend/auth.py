## This class contains authorization methods and routes for the Spring 2024 CS 4550 Pony Express application.
# Author: Riley Kraabel

import os
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlmodel import Session, SQLModel, select

from backend import database as db
from backend.entities import UserInDB, UserResponse
from backend.database import DuplicateEntityException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_token_duration = 3600
jwt_alg = "HS256"
jwt_key = os.environ.get(
    "JWT_KEY", 
    default="riley",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# ------- models ------------------- #
class UserRegistration(SQLModel):
    """Request Model to register new user."""
    username: str
    email: str
    password: str

class AccessToken(BaseModel):
    """Response model for access token. """
    access_token: str
    token_type: str
    expires_in: int

class Claims(BaseModel):
    """Access token claims (aka payload)."""
    sub: str
    exp: int

# ----------------- exceptions ------------------- #
class AuthException(HTTPException):
    def __init__(self, error: str, description: str):
        super().__init__(
            status_code=401,
            detail={
                "error": error,
                "error_description": description
            }
        )

class InvalidCredentials(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="invalid username or password",
        )

class InvalidToken(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="invalid access token",
        )

class ExpiredToken(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="expired access token",
        )

# ----------------- routes -------------------------- #
@auth_router.post("/registration", response_model=UserResponse, status_code=201)
def register_new_user(
    registration: UserRegistration,
    session: Annotated[Session, Depends(db.get_session)]
):
    existing_user = db.get_existing_user(session, registration.username, registration.email)
    if existing_user:
        raise DuplicateEntityException(entity_name="User",
                                       entity_field="username" if existing_user.username == registration.username else "email",
                                       entity_value=registration.username if existing_user.username == registration.username else registration.email)

    hashed_password = pwd_context.hash(registration.password)
    new_user = UserInDB(username=registration.username, email=registration.email, hashed_password=hashed_password)
    user = db.create_user(new_user, session)
    return UserResponse(user=user)

@auth_router.post("/token", response_model=AccessToken)
def get_access_token(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(db.get_session)
):
    user = _get_authenticated_user(session, form)
    return _build_access_token(user)

# ----------- helper methods ------------------ #
def get_current_user(
    session: Session = Depends(db.get_session),
    token: str = Depends(oauth2_scheme),
) -> UserInDB:
    user = _decode_access_token(session, token)
    return user

def _get_authenticated_user(
    session: Session,
    form: OAuth2PasswordRequestForm
) -> UserInDB:
    user = session.exec(select(UserInDB).where(UserInDB.username == form.username)).first()

    if user is None or not pwd_context.verify(form.password, user.hashed_password):
        raise InvalidCredentials
    
    return user

def _build_access_token(user: UserInDB) -> AccessToken:
    expiration = int(datetime.now(timezone.utc).timestamp()) + access_token_duration
    claims = Claims(sub=str(user.id), exp=expiration)
    access_token = jwt.encode(claims.model_dump(), key=jwt_key, algorithm=jwt_alg)

    return AccessToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=access_token_duration
    )

def _decode_access_token(
    session: Session, 
    token: str
) -> UserInDB:
    try:
        claims_dict = jwt.decode(token, key=jwt_key, algorithms=[jwt_alg])
        claims = Claims(**claims_dict)
        user_id = claims.sub
        user = session.get(UserInDB, user_id)

        if user is None:
            raise InvalidToken()
        
        return user
    
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()
    except ValidationError:
        raise InvalidToken()