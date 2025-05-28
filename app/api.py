from fastapi import APIRouter, Depends

from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse, StreamingResponse, Response, FileResponse
from starlette.status import HTTP_202_ACCEPTED

from models import Books
from database import get_session


from pydantic import BaseModel
from typing import Optional



router = APIRouter()


class BookCreate(BaseModel):
    bookname: str
    author: str
    year_of_publication: int
    isbn: Optional[str] = None
    quantity: int = 1


@router.post("/creat_book")
def create_book(book: BookCreate, db: Session = Depends(get_session)):
    db_book = Books(
        bookname=book.bookname,
        author=book.author,
        year_of_publication=book.year_of_publication,
        isbn=book.isbn,
        quantity=book.quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return Response(status_code=status.HTTP_201_CREATED)


@router.get("/read_books")
def read_books(db: Session = Depends(get_session)):
    db_books = db.query(Books).all()
    return db_books