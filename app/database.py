from sqlmodel import create_engine, Session

sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False, "timeout": 30}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()