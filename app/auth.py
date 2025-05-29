from starlette.responses import Response                          # Импортируем класс Response для отправки HTTP ответов
from database import get_session                                  # Импортируем функцию для получения сессии
from fastapi import Depends, HTTPException, status, APIRouter     # Импортируем необходимые инструменты FastAPI
from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)          # Импортируем механизмы аутентификации
from sqlalchemy.orm import Session                                # Импортируем сессию для работы с базой данных
from jose import JWTError, jwt                                    # Импортируем библиотеки для работы с JWT
from passlib.context import CryptContext                          # Импортируем библиотеку для хеширования паролей
from typing import Optional                                       # Импортируем тип Optional для аннотаций
from models import User, Readers                                  # Импортируем модели User и Readers
from datetime import datetime, timedelta                          # Импортируем классы для работы с датами и временем


# Константы для настройки JWT
SECRET_KEY = "your_secret_key"                                    # Секретный ключ для подписи токенов
ALGORITHM = "HS256"                                               # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = 10                                  # Время жизни токена в минутах(можно изменить)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Создаем экземпляр маршрутизатора
router = APIRouter()

# Функция для хеширования пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Функция для создания JWT токена
def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для получения текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Роут для регистрации нового пользователя
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(username: str, password: str, email: str, db: Session = Depends(get_session)):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username}

# Роут для получения токена доступа
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Роут для получения информации о текущем пользователе
@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return {"email": user.email}


# Роут для создания нового читателя
@router.get("/creat_readers")
async def create_readers(readername: str, email: str, db: Session = Depends(get_session)):
    db_reader = Readers(readername=readername, email=email)
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader


# Роут для удаления читателя
@router.delete("/readers/{readers_id}")
async def delete_readers(readers_id: int, db: Session = Depends(get_session)):
    db_reader = db.query(Readers).filter(Readers.id == readers_id).first()
    if db_reader is None:
        raise HTTPException(status_code=404)
    db.delete(db_reader)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

