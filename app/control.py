from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session

from starlette.exceptions import HTTPException


from models import Books, BorrowedBooks
from database import get_session



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