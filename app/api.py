from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import  Response
from models import Books
from database import get_session
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class BookCreate(BaseModel):
    bookname: str
    author: str
    year_of_publication: int
    isbn: Optional[str] = None
    quantity: int = 1


class BookResponse(BaseModel):
    id: int
    bookname: str
    author: str
    year_of_publication: int
    isbn: Optional[str]
    quantity: int

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


@router.get("/read_books", response_model=List[BookResponse])
def read_books(
        id: Optional[int] = Query(None),
        bookname: Optional[str] = Query(None),
        db: Session = Depends(get_session)
):
    query = db.query(Books)

    if id is not None:
        query = query.filter(Books.id == id)
    if bookname is not None:
        query = query.filter(
            Books.bookname.ilike(f"%{bookname}%"))

    db_books = query.all()

    if not db_books:
        raise HTTPException(status_code=404, detail="Book not found")

    return db_books


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_session)):
    db_book = db.query(Books).filter(Books.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.dict().items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)

    return Response(status_code=status.HTTP_200_OK)


@router.delete("/books/{book_id}", response_model=BookResponse)
def delete_book(book_id: int, db: Session = Depends(get_session)):
    db_book = db.query(Books).filter(Books.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
