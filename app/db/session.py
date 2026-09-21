from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

DATABASE_URL = 'sqlite:///./shop.db'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# if __name__ == "__main__":
#     from app.db.base import Base
#     Base.metadata.create_all(bind=engine)

#     gen = get_db()
#     session = next(gen)
#     print(type(session))   # <class 'sqlalchemy.orm.session.Session'>
#     try:
#         next(gen)
#     except StopIteration:
#         pass