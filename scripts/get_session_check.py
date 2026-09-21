if __name__ == "__main__":
    from app.db.session import engine, get_db
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)

    gen = get_db()
    session = next(gen)
    print(type(session))   # <class 'sqlalchemy.orm.session.Session'>
    try:
        next(gen)
    except StopIteration:
        pass