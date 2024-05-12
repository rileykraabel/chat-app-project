## This class contains backend database methods for the Spring 2024 CS 4550 Pony Express application.
# Author: Riley Kraabel

from sqlmodel import Session, SQLModel, create_engine, select
from fastapi import HTTPException
from datetime import datetime
from backend.entities import (
    MessageInDB,
    UserInDB,
    ChatInDB,
    Message,
    UserUpdate,
    UserChatLinkInDB
)

engine = create_engine(
    "sqlite:///backend/pony_express.db",
    echo=True,
    connect_args={"check_same_thread": False},
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
    
class EntityNotFoundException(Exception):
    def __init__(self, *, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id

class DuplicateEntityException(HTTPException):
    def __init__(self, *, entity_name: str, entity_field: str, entity_value: str):
        self.entity_name = entity_name
        self.entity_field = entity_field
        self.entity_value = entity_value

        super().__init__(
            status_code=422,
            detail={
                "type": "duplicate_value",
                "entity_name": entity_name,
                "entity_field": entity_field,
                "entity_value": entity_value
            }
        )

# ---------- methods for the 'users' routes ----------- #
def get_user_by_id(user_id: int, session: Session) -> UserInDB:
    """
    Retrieve a user from the database.

    :param user_id - id of the user to be retrieved. 
    :param session - a Session object for database retrieval. 
    :raises EntityNotFoundException if the user_id does not map to anything in the database.
    :return - the retrieved user. 
    """
    user = session.get(UserInDB, user_id)
    if user:
        return user

    raise EntityNotFoundException(entity_name="User", entity_id=user_id)        

def get_all_users(session: Session) -> list[UserInDB]:
    """
    Retrieve all users from the database. 

    :param session - a Session object for database retrieval. 
    :return - ordered list of users.
    """
    return session.exec(select(UserInDB)).all()

def get_all_users_from_chat(chat_id: int, session: Session) -> list[UserInDB]:
    """
    Retrieve all of the users involved in the 'chat_id' provided.

    :param chat_id - the id of the chat to be retrieved.
    :param session - a Session object for database retrieval. 
    :return - list of the users involved in the specified 'chat_id'. 
    :raises EntityNotFoundException if the chat_id does not map to anything in the database. 
    """
    chat = get_chat_by_id(chat_id, session)
    return chat.users

def create_user(user_create: UserInDB, session: Session) -> UserInDB:
    """
    Creates a new user in the database. 

    :param user_create - attributes of the user to be created. 
    :param session - a Session object for database retrieval. 
    :return - the newly created user.  
    """
    user = UserInDB(**user_create.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user(user: UserInDB, user_update: UserUpdate, session: Session) -> UserInDB:
    """
    Updates an existing user in the database.

    :param user - the User object to update.
    :param user_update - the attributes of the user to update.
    :param session - a Session object for database retrieval. 
    :return - the updated version of the user. 
    """
    current_user = get_user_by_id(user.id, session)
    for attr, value in user_update.model_dump(exclude_none=True).items():
        setattr(current_user, attr, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

def get_existing_user(session: Session, username: str, email: str) -> UserInDB:
    """
    Retrieves a user from the database if they exist. 

    :param session - a Session object for database retrieval. 
    :param username - the username to check for in the database.
    :param email - the email to check for in the database.
    :return - the user if they exist. 
    """
    return session.exec(select(UserInDB).filter((UserInDB.username == username) | (UserInDB.email == email))).first()

# ---------- methods for the 'chats' routes  ----------- #
def get_chat_by_id(chat_id: int, session: Session) -> ChatInDB:
    """
    Retrieve a chat from the database using the specified chat id. 

    :param chat_id - id of the chat to find. 
    :param session - a Session object for database retrieval. 
    :raises EntityNotFoundException if the chat_id does not map to anything in the database. 
    :return - the retrieved chat.
    """
    chat = session.get(ChatInDB, chat_id)
    if chat:
        return chat
    
    raise EntityNotFoundException(entity_name="Chat", entity_id=chat_id)

def get_all_chats(current_user: UserInDB, session: Session) -> list[ChatInDB]:
    """
    Retrieve all chats from the database that the given user is a part of.

    :param current_user - the currently logged in user.
    :param session - a Session object for database retrieval. 
    :return - ordered list of chats.
    """
    valid_chats = []
    all_chats = session.exec(select(ChatInDB)).all()
    for chat in all_chats:
        chat_link = session.get(UserChatLinkInDB, (current_user.id, chat.id))
        if chat_link is not None:
            valid_chats.append(chat)
    
    return valid_chats

def add_chat(chat_name: str, current_user: UserInDB, session: Session) -> ChatInDB:
    """
    Adds a chat to the database. The current user is set to be the chat's owner, and they are added
    as a member of the chat. 

    :param chat_name - the new name of the chat being added.
    :param current_user - the currently logged in user, who will be the owner of the new chat.
    :param session - a Session object for database retrieval.
    :return - the newly added chat.
    """
    new_chat = ChatInDB(
        name=chat_name,
        owner_id=current_user.id
    )
    new_chat.users.append(current_user)
    session.add(new_chat)
    session.commit()
    session.refresh(new_chat)

    chat_link = session.get(UserChatLinkInDB, (current_user.id, new_chat.id))
    if chat_link is None:
        session.add(chat_link)
        session.commit()

    return new_chat

def update_chat(chat_id: int, new_name: str, session: Session) -> ChatInDB:
    """
    Update a chat in the database.

    :param chat_id: id of the chat to be updated
    :param chat_update: attributes to be updated on the chat
    :param session - a Session object for database retrieval. 
    :return: the updated chat
    """
    chat = get_chat_by_id(chat_id, session)
    chat.name = new_name

    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat

def add_new_chat_user(chat_id: int, user_id: int, session: Session) -> ChatInDB:
    """
    Add a new user to the specified chat.
    Adds a row to the user_chat_links table with the specified user_id and chat_id if a row does not already exist.

    :param chat_id - id of the chat to be updated.
    :param user_id - id of the new user being added to the chat.
    :param session - a Session object for database retrieval.
    :return - the updated chat containing the new user.
    """
    chat = get_chat_by_id(chat_id, session)
    user = get_user_by_id(user_id, session)
    chat.users.append(user)

    statement = select(UserChatLinkInDB).where(
        UserChatLinkInDB.user_id == user.id, 
        UserChatLinkInDB.chat_id == chat.id
    )
    existing_link = session.exec(statement).all()
    if not existing_link:
        session.add(existing_link)
        session.commit()

    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat

def remove_chat_user(chat_id: int, user_id: int, session: Session) -> ChatInDB:
    """
    Removes a user from the specified chat.
    Removes a row to the user_chat_links table with the specified user_id and chat_id if one exists.

    :param chat_id - id of the chat to be updated.
    :param user_id - id of the user to be removed from the chat.
    :param session - a Session object for database retrieval.
    :return - the updated chat without the user who has been removed.
    """
    chat = get_chat_by_id(chat_id, session)
    user = get_user_by_id(user_id, session)
    chat.users.remove(user)

    statement = select(UserChatLinkInDB).where(
        UserChatLinkInDB.user_id == user.id, 
        UserChatLinkInDB.chat_id == chat.id
    )
    existing_link = session.exec(statement).all()

    if existing_link is not None:
        session.delete(existing_link)
        session.commit()
    
    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat
    
def delete_chat(chat_id: int, session: Session):
    """
    Delete a chat from the database.

    :param chat_id: the id of the chat to be deleted
    :param session - a Session object for database retrieval. 
    """
    chat = get_chat_by_id(chat_id, session)
    session.delete(chat)
    session.commit()

# ------------------ methods for routes handling 'messages' ------------------- #
def get_message_by_id(message_id: int, session: Session) -> MessageInDB:
    """
    Retrieve a message from the database using the specified message id.

    :param message_id - id of the message to find.
    :param session - a Session object for database retrieval.
    :raises EntityNotFoundexception if the message_id does not map to anything in the database.
    :return - the retrieved message.
    """
    message = session.get(MessageInDB, message_id)
    if message:
        return message
    
    raise EntityNotFoundException(entity_name="Message", entity_id=message_id)

def get_all_messages_from_chat(chat_id: int, session: Session) -> list[Message]:
    """
    Retrieve all messages for a given chat's 'chat_id'. 

    :param chat_id - the id of the chat to be retrieved.
    :param session - a Session object for database retrieval. 
    :return - list of all messages from the specified 'chat_id'. 
    :raises EntityNotFoundException if the chat_id does not map to anything in the database. 
    """
    chat = get_chat_by_id(chat_id, session)
    return [Message(id=message_in_db.id, text=message_in_db.text, chat_id=chat_id, user=message_in_db.user, 
                   created_at=message_in_db.created_at) for message_in_db in chat.messages]

def send_message(new_message: str, user: UserInDB, chat_id: int, session: Session) -> MessageInDB:
    """
    Sends a new message within the specified chat_id. 

    :param chat_id - id of the chat to send the message to.
    :param message - the new message to send within the chat.
    :param user - the currently logged in user who is sending the new message.
    :param session - a Session object for database retrieval. 
    :return - a Message object containing the description of the newly sent message.
    """
    chat = get_chat_by_id(chat_id, session)
    new_message = MessageInDB(
        text=new_message,
        user=user,
        chat_id=chat.id,
        created_at=datetime.now()
    )

    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return new_message

def update_message(message_id: int, new_message: str, session: Session) -> MessageInDB:
    """
    Updates an existing message in the database.

    :param message_id - id of the message to update.
    :param message_update - the attributes of the message to update.
    :param session - a Session object for database retrieval.
    :return - the update version of the message.
    """
    current_message = get_message_by_id(message_id, session)
    current_message.text = new_message

    session.add(current_message)
    session.commit()
    session.refresh(current_message)

    return current_message

def delete_message(message_id: int, session: Session):
    """
    Deletes the specified message from the database if it exists and other criteria is met.

    :param message_id - id of the message to delete.
    :param session - a Session object for database retrieval.
    """
    current_message = get_message_by_id(message_id, session)
    session.delete(current_message)
    session.commit()

# --------------- methods for routes handling 'members' / access rights ------------------- #
def is_member_of_chat(chat_id: int, current_user: UserInDB, session: Session) -> bool:
    """
    Checks if the current_user is a member of the specified chat.

    :param chat_id - id representing the chat.
    :param current_user - the currently logged in user.
    :param - a Session object for database retrieval.
    :returns - a UserChatLinkInDB object representing the connection between the user/chat.
    :raises - NoPermission error if the user is not a member of the chat.
    """
    chat = get_chat_by_id(chat_id, session)
    if chat:
        link = session.get(UserChatLinkInDB, (current_user.id, chat.id))
        if link:
            return True
        
        raise HTTPException(status_code=403, detail={
            "error": "no_permission",
            "error_description": "requires permission to view chat"
        })
    
def is_owner_of_chat(chat_id: int, current_user: UserInDB, session: Session) -> bool:
    """
    Checks if the current_user is the owner of the specified chat.

    :param chat_id - id representing the chat.
    :param current_user - the currently logged in user.
    :param - a Session object for database retrieval.
    :returns - bool True if the current_user is the owner.
    :raises - NoPermission error if the user is not the owner of the chat.
    """
    chat = get_chat_by_id(chat_id, session)
    if chat.owner_id == current_user.id:
        return True
    
    raise HTTPException(status_code=403, detail={
            "error": "no_permission",
            "error_description": "requires permission to edit chat"
        })

def is_owner_of_message(message_id: int, current_user: UserInDB, session: Session) -> bool:
    """
    Checks if the current_user is the owner of the specified message.

    :param message_id - int representing the message.
    :param current_user - the currently logged in user.
    :param session - a Session object for database retrieval.
    :returns - bool True if the current_user is the owner.
    :raises - NoPermission error if the user is not the owner of the message.
    """
    message = get_message_by_id(message_id, session)
    if message.user_id == current_user.id:
        return True
    
    raise HTTPException(status_code=403, detail={
        "error": "no_permission",
        "error_description": "requires permission to edit message"
    })

def owner_update_chat_members(chat_id: int, current_user: UserInDB, session: Session) -> bool:
    """
    Checks if the current_user is the owner of the specified chat.

    :param chat_id - id representing the chat.
    :param current_user - the currently logged in user.
    :param - a Session object for database retrieval.,l
    :returns - a ChatInDB object if the current_user is the owner.
    :raises - NoPermission error if the user is not the owner of the chat.
    """
    chat = get_chat_by_id(chat_id, session)
    if chat.owner_id == current_user.id:
        return True
    
    raise HTTPException(status_code=403, detail={
            "error": "no_permission",
            "error_description": "requires permission to edit chat members"
        })

def check_remove_owner(chat_id: int, user_id: int, session: Session) -> bool:
    """
    Checks if the given user_id is the owner of the given chat_id. 
    If the user is the owner, the method returns False, so the user cannot be removed. Otherwise, returns True.

    :param chat_id - id representing the chat.
    :param user_id - id representing the user.
    :param session - a Session object for database retrieval. 
    :returns - bool True if the user_id is not the owner of the chat.
    :raises - a NoPermission error signifying the user cannot be removed, as they are the owner of the chat.
    """

    chat = get_chat_by_id(chat_id, session)
    user = get_user_by_id(user_id, session)

    if chat.owner_id != user.id:
        return True
    
    raise HTTPException(status_code=422, detail={
            "error": "invalid_state",
            "error_description": "owner of a chat cannot be removed"
        })