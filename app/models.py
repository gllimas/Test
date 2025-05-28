from typing import Optional

# from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field


Base = SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    def __repr__(self):
        return f"<User (username={self.username})>"


class Books(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bookname: str = Field(unique=True, index=True, nullable=False)
    author: str = Field(unique=True, index=True, nullable=False)
    year_of_publication: Optional[int]
    isbn: Optional[str]
    quantity: int = Field(default=1, ge=0)