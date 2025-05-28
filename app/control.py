from datetime import datetime, date
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session

from starlette.exceptions import HTTPException

from auth import get_current_user
from models import Books, BorrowedBooks
from database import get_session

class BookBorrowedResponse(BaseModel):
    book_id: int
    bookname: str
    author: str
    borrow_date: date



router = APIRouter()


@router.get("/issue_a_book")
async def issue_book(book_id: int, reader_id: int, db: Session = Depends(get_session)):
    # Получаем книгу по ID
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    if book.quantity <= 0:
        raise HTTPException(status_code=400, detail="Нет доступных экземпляров книги")

    active_borrows_count = db.query(func.count(BorrowedBooks.id)).filter(
        BorrowedBooks.reader_id == reader_id,
        BorrowedBooks.return_date.is_(None)
    ).scalar()

    if active_borrows_count >= 3:
        raise HTTPException(status_code=400, detail="Читатель уже взял 3 книги и не вернул их.")

    book.quantity -= 1

    borrowed_record = BorrowedBooks(
        book_id=book.id,
        reader_id=reader_id,
        borrow_date=datetime.utcnow(),
        return_date=None
    )


    db.add(book)
    db.add(borrowed_record)
    db.commit()

    return {"message": f"Книга '{book.bookname}' выдана читателю с ID {reader_id}"}

@router.get("/return_book")
async def return_book(book_id: int, reader_id: int, db: Session = Depends(get_session)):
    borrowed_record = db.query(BorrowedBooks).filter(
        BorrowedBooks.book_id == book_id,
        BorrowedBooks.reader_id == reader_id,
        BorrowedBooks.return_date.is_(None)
    ).first()
    if not borrowed_record:
        raise HTTPException(status_code=404,)

    borrowed_record.return_date = datetime.utcnow()
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404,)
    book.quantity += 1
    db.add(book)
    db.add(borrowed_record)
    db.commit()
    return {"massage": f" Книга '{book.bookname}' возвращена"}



@router.get("/reader/{reader_id}/borrowed_books", response_model=List[BookBorrowedResponse])
async def get_borrowed_books_for_reader(
    reader_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):

    borrowed_records = (
        db.query(BorrowedBooks)
        .filter(
            BorrowedBooks.reader_id == reader_id,
            BorrowedBooks.return_date.is_(None)  # еще не возвращены
        )
        .all()
    )

    if not borrowed_records:
        return []

    book_ids = [record.book_id for record in borrowed_records]

    books = (
        db.query(Books)
        .filter(Books.id.in_(book_ids))
        .all()
    )

    response = []
    for record in borrowed_records:
        book_info = next((b for b in books if b.id == record.book_id), None)
        if book_info:
            response.append(
                BookBorrowedResponse(
                    book_id=book_info.id,
                    bookname=book_info.bookname,
                    author=book_info.author,
                    borrow_date=record.borrow_date.date()  # или оставить datetime
                )
            )
    return response