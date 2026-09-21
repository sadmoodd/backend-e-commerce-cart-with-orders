from app.db import models
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(engine)
