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

