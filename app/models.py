from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


Base = SQLModel

# Модель для User
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    def __repr__(self):
        return f"<User (username={self.username})>"


# Модель для книги
class Books(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bookname: str = Field(unique=True, index=True, nullable=False)
    author: str = Field(unique=True, index=True, nullable=False)
    year_of_publication: Optional[int]
    isbn: Optional[str]
    quantity: int = Field(default=1, ge=0)




# модель для читателя
class Readers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    readername: str = Field(unique=None, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)


# модель для таблицы кто взял книгу и какую
class BorrowedBooks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int
    reader_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = Field(default=None, nullable=True)