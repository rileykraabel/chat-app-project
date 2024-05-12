## This class contains backend entity structures for the Spring 2024 CS 4550 Pony Express application.
# Author: Riley Kraabel

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import Field, Relationship, SQLModel

# Represents Metadata for any collection other than Chats. 
class Metadata(BaseModel):
    count: int

# Represents Metadata for a Chat collection. 
class ChatMetadata(BaseModel):
    message_count: int
    user_count: int

# Represents the Database model for a UserChatLink item. 
class UserChatLinkInDB(SQLModel, table=True):
    """Database model for many-to-many relation of users to chats."""

    __tablename__ = "user_chat_links"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", primary_key=True)

# Represents the Database model for a User item. 
class UserInDB(SQLModel, table=True):
    """Database model for user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    chats: list["ChatInDB"] = Relationship(
        back_populates="users",
        link_model=UserChatLinkInDB,
    )

# Represents the Database model for a Chat item. 
class ChatInDB(SQLModel, table=True):
    """Database model for chat."""

    __tablename__ = "chats"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    owner: UserInDB = Relationship()
    users: list[UserInDB] = Relationship(
        back_populates="chats",
        link_model=UserChatLinkInDB,
    )
    messages: list["MessageInDB"] = Relationship(back_populates="chat")

# Represents the Database model for a Message item. 
class MessageInDB(SQLModel, table=True):
    """Database model for message."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    user_id: int = Field(foreign_key="users.id")
    chat_id: int = Field(foreign_key="chats.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    user: UserInDB = Relationship()
    chat: ChatInDB = Relationship(back_populates="messages")

# Represents a data model object for a user. 
class User(SQLModel):
    id: int
    username: str
    email: str
    created_at: datetime

# Represents a data model object for a chat.
class Chat(SQLModel):
    id: int
    name: str
    owner: User
    created_at: datetime

# Represents a data model object for a message. 
class Message(SQLModel):
    id: int
    text: str
    chat_id: int
    user: User
    created_at: datetime

# Represents an API response for a user. 
class UserResponse(BaseModel):
    user: User

# Represents the API response for creating a new message. 
class CreateMessage(BaseModel):
    text: str
    
# Represents an API response for a chat.
class ChatResponse(BaseModel):
    chat: Chat

# Represents an API response for the get-chat route. 
class GetChatResponse(BaseModel):
    meta: ChatMetadata
    chat: Chat
    messages: Optional[list[Message]] = Field(default=None)
    users: Optional[list[User]] = Field(default=None)

# Represents an API response for a message. 
class MessageResponse(BaseModel):
    message: Message

# Represents an API response for a collection of users, but structured for when removing a user. 
class RemovedUserCollection(BaseModel):
    users: list[User]

# Represents an API response for a collection of users.
class UserCollection(BaseModel):
    meta: Metadata
    users: list[User]

# Represents an API response for a collection of chats.
class ChatCollection(BaseModel):
    meta: Metadata
    chats: list[Chat]

# Represents a collection of messages.
class MessageCollection(BaseModel):
    meta: Metadata
    messages: list[Message]

# Represents parameters for updating a user in the system.
class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)

class ChatUpdate(BaseModel):
    name: str

class ChatCreate(BaseModel):
    name: str

class MessageCreate(BaseModel):
    text: str