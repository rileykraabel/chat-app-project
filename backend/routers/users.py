from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend import database as db
from backend.auth import get_current_user, InvalidToken
from backend.entities import (   
    UserInDB, 
    UserCollection,
    UserResponse,
    ChatCollection,
    UserUpdate
)

users_router = APIRouter(prefix="/users", tags=["Users"])

# Returns the user currently logged in. 
@users_router.get("/me", response_model=UserResponse, description="Returns the current user.")
def get_current_user(user: UserInDB = Depends(get_current_user)):
    return UserResponse(user=user)

# Updates the currently logged in user's username or email, depending on their choice. 
@users_router.put("/me", response_model=UserResponse, status_code=200, description="Updates the username/email of the current user.")
def update_current_user(user_update: UserUpdate, user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    if user:
        return UserResponse(user=db.update_user(user, user_update, session))
    
    raise InvalidToken()

# Returns a list of users sorted by id (str), along with a count of all users (int).
@users_router.get("", response_model=UserCollection, description="Get all users from the system, along with a count.")
def get_all_users(session: Session = Depends(db.get_session)):
    users = db.get_all_users(session)
    return UserCollection(meta={"count": len(users)}, 
                          users=sorted(users, key=lambda user: user.id))

# If the user exists, returns a user for a given user id (str). If they do not exist, returns a 404 HTTP status code.
@users_router.get("/{user_id}", response_model=UserResponse, description="Get a user from a given id.")
def get_user_by_id(user_id: int, session: Session = Depends(db.get_session)):
    return UserResponse(user=db.get_user_by_id(user_id, session))

# Returns a list of chats for a given user (by user id), along with a count of the total of chats sent (int). 
@users_router.get("/{user_id}/chats", response_model=ChatCollection, description="Returns a list of chats for a given user, found by user id.")
def get_user_chats(user_id: int, session: Session = Depends(db.get_session)):
    user = db.get_user_by_id(user_id, session)
    return ChatCollection(meta={"count": len(user.chats)},
                          chats=user.chats)