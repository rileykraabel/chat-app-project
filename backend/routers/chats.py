## This class contains backend methods for the Spring 2024 CS 4550 Pony Express application.
# Author: Riley Kraabel

from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlmodel import Session
from backend import database as db
from backend.auth import get_current_user
from backend.entities import (
    ChatMetadata,
    UserInDB,
    MessageResponse,
    GetChatResponse,
    ChatCollection,
    ChatResponse,
    UserCollection,
    MessageCollection,
    CreateMessage,
    ChatCreate,
    ChatUpdate,
    RemovedUserCollection,
    MessageCreate
)

##### note: need to adjust the backend router methods to account for different access status codes ****

chats_router = APIRouter(prefix="/chats", tags=["Chats"])

## ------------------ assignment 5b methods ---------------- ##
# Adds a new chat to the database using the input chat_name and currently logged in user. 
@chats_router.post("", status_code=201, response_model=ChatResponse, description="Adds a new chat with the current user as the owner.")
def add_new_chat(new_chat: ChatCreate, 
                 current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    return ChatResponse(chat=db.add_chat(new_chat.name, current_user, session))

# If the chat exists and the current user is the owner of it, updates its' chat name. 
# If it does not exist, retruns a 404 HTTP status code. 
@chats_router.put("/{chat_id}", response_model=ChatResponse, description="If the chat exists and the current user is the owner, updates the name.")
def update_chat(chat_id: int, chat_update: ChatUpdate, 
                current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chat = db.get_chat_by_id(chat_id, session)
    if chat:
        if db.is_member_of_chat(chat.id, current_user, session):
            if db.is_owner_of_chat(chat.id, current_user, session):
                return ChatResponse(chat=db.update_chat(chat.id, chat_update.name, session))
        
# If the chat exists and the user to be added exists, they are added to the list of users for the chat.
# If it does not exist, returns a 404 HTTP status code.
@chats_router.put("/{chat_id}/users/{user_id}", status_code=201, response_model=UserCollection, description="If the current user is the owner of the specified chat, adds a new user to the chat.")
def add_new_chat_user(chat_id: int, user_id: int,
                      current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chat = db.get_chat_by_id(chat_id, session)
    new_user = db.get_user_by_id(user_id, session)
    if chat and new_user:
        # ensure the user is a member of the chat
        if db.is_member_of_chat(chat.id, current_user, session): 
            # ensure they are also the owner
            if db.owner_update_chat_members(chat.id, current_user, session):
                updated_chat = db.add_new_chat_user(chat.id, new_user.id, session)
                users = users=db.get_all_users_from_chat(updated_chat.id, session)
                return UserCollection(meta={"count": len(users)}, users=users)
        
# If the chat exists and the current user is the owner of it, removes the specified user from the chat.
# If it does not exist, returns a 404 HTTP status code.
@chats_router.delete("/{chat_id}/users/{user_id}", status_code=200, response_model=RemovedUserCollection, description="If the current user is the owner of the specified chat, removes the specified user from the chat.")
def remove_user_from_chat(chat_id: int, user_id: int, 
                          current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chat = db.get_chat_by_id(chat_id, session)
    removed_user = db.get_user_by_id(user_id, session)
    if chat and removed_user:
        # ensure the user is a member of the chat
        if db.is_member_of_chat(chat.id, current_user, session):
            # ensure they are also the owner
            if db.owner_update_chat_members(chat.id, current_user, session):
                # ensure the user being removed is not the owner of the chat
                if db.check_remove_owner(chat.id, removed_user.id, session):
                    updated_chat = db.remove_chat_user(chat.id, removed_user.id, session)
                    users = db.get_all_users_from_chat(updated_chat.id, session)
                    return RemovedUserCollection(users=users)


## ------------------- assignment 5c methods ----------------- ##
# If the chat exists, the message exists, and the current user is the owner of the message, updates the message text.
# If it does not exist, returns a 404 HTTP status code.
@chats_router.put("/{chat_id}/messages/{message_id}", status_code=200, response_model=MessageResponse, description="If the chat exists, the message exists, and the current user is the owner of the message, they can update its' contents.")
def update_message(chat_id: int, message_id: int, message_create: MessageCreate, 
                   current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chat = db.get_chat_by_id(chat_id, session)
    if chat: 
        message = db.get_message_by_id(message_id, session)
        if message:
            if db.is_owner_of_message(message.id, current_user, session):
                return MessageResponse(message=db.update_message(message.id, message_create.text, session))
            
# If the chat exists, the message exists, and the current user if the owner of the message, deletes the message.
# If it does not exist, returns a 404 HTTP status code.
@chats_router.delete("/{chat_id}/messages/{message_id}", status_code=204, description="If the chat exists, the message exists, and the current user is the message owner, the user can delete their message.")
def delete_message(chat_id: int, message_id: int,
                   current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chat = db.get_chat_by_id(chat_id, session)
    if chat: 
        message = db.get_message_by_id(message_id, session)
        if message:
            if db.is_owner_of_message(message.id, current_user, session):
                db.delete_message(message.id, session)

# Returns a list representation of all chats the currently logged in user is apart of.
@chats_router.get("", response_model=ChatCollection, description="Returns a list of chats the current user is in, sorted by the name of the chat, along with the number of chats.")
def get_all_chats(current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    chats = db.get_all_chats(current_user, session)
    if len(chats) > 0:
        return ChatCollection(meta={"count": len(chats)}, chats=sorted(chats, key=lambda chat: chat.id))
    
    return ChatCollection(meta={"count": len(chats)}, chats=[])

# If the chat exists, return the chat for the given id (int) The user is allowed to specify additional data they want returned. 
# If it does not exist, returns a 404 HTTP status code.
@chats_router.get("/{chat_id}", status_code=200, response_model=GetChatResponse, response_model_exclude_none=True, description="If the chat with the specified id exists and the current user is a member, it is returned.")
def get_chat(chat_id: int, 
             include: Optional[list[str]] = Query(None, description="Include additional data (e.g., users or messages) in the response."),
             current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    if db.is_member_of_chat(chat_id, current_user, session):
        chat = db.get_chat_by_id(chat_id, session)
        metadata = ChatMetadata(message_count=len(chat.messages), user_count=len(chat.users))
        chat_response = GetChatResponse(meta=metadata, chat=chat)

        if include:
            if "messages" in include:
                chat_response.messages = db.get_all_messages_from_chat(chat_id, session)
            if "users" in include:
                chat_response.users = chat.users

        return chat_response

# If the chat exists, returns a list of messages for the chat using the given id (str), along with a count of the messages in the chat (int). 
# If it does not exist, returns a 404 HTTP status code. 
@chats_router.get("/{chat_id}/messages", response_model=MessageCollection, description="If the chat exists and the current user is a member, return a list of messages using the input id.")
def get_messages_from_chat(chat_id: int, 
                           current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    if db.is_member_of_chat(chat_id, current_user, session):
        chat = db.get_chat_by_id(chat_id, session)
        return MessageCollection(meta={"count": len(chat.messages)},
                             messages=chat.messages)

# If the chat exists, returns a list of the users for the chat using the given id (str), along with a count of the number of users in the chat (int). 
# If it does not exist, returns a 404 HTTP status code.
@chats_router.get("/{chat_id}/users", response_model=UserCollection, description="If the chat exists and the current user is a member, returns a list of the users in the input chat id.")
def get_users_from_chat(chat_id: int, 
                        current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    if db.is_member_of_chat(chat_id, current_user, session):
        chat = db.get_chat_by_id(chat_id, session)
        return UserCollection(meta={"count": len(chat.users)}, users=chat.users)

# If a chat with the specified chat_id exists and the current user is a member of the chat, adds a new message within the chat. 
# If it does not exist, returns a 404 HTTP status code.
@chats_router.post("/{chat_id}/messages", status_code=201, response_model=MessageResponse, description="If the chat exists and the current user is a member, creates a new message in the specified chat.")
def add_new_message(chat_id: int, new_message: CreateMessage,
                    current_user: UserInDB = Depends(get_current_user), session: Session = Depends(db.get_session)):
    if db.is_member_of_chat(chat_id, current_user, session):
        chat = db.get_chat_by_id(chat_id, session)
        if chat: 
            return MessageResponse(message=db.send_message(new_message.text, current_user, chat.id, session))