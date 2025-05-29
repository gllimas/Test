from fastapi import FastAPI, Request                               # Импортируем необходимые классы и функции из FastAPI
from sqlmodel import SQLModel                                      # Импортируем SQLModel для работы с базой данных
from starlette.middleware import Middleware                        # Импортируем Middleware для управления
                                                                   # промежуточными слоями
from starlette.middleware.cors import CORSMiddleware               # Импортируем CORS Middleware для настройки CORS
from fastapi.templating import Jinja2Templates                     # Импортируем Jinja2 для работы с шаблонами
from starlette.responses import HTMLResponse                       # Импортируем HTMLResponse для отправки HTML ответов


import auth, api, control                                          # импортируем файлы

from database import engine                                        # импорт базы данных

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]


templates = Jinja2Templates(directory="templates")                 # Инициализируем Jinja2

def create_db_and_tables():                                        # Создаем таблицы
    SQLModel.metadata.create_all(engine)


# Создаем приложения FastAPI
app = FastAPI(middleware=middleware, title='Test', description='FastAPI')


# Подключаем маршрутизаторы
app.include_router(auth.router, tags=["AUTH"], prefix="/auth")
app.include_router(api.router, tags=["API"], prefix="/api")
app.include_router(control.router, tags=["Control"], prefix="/control")

create_db_and_tables()                                             # Создаем базу данных при запуске


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



# Запускаем приложение
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)