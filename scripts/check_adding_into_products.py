from app.db.session import SessionLocal
from app.db.models.product import ProductModel
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

db = SessionLocal()
p = ProductModel(
    name="Test",
    price=Decimal("100"),
    stock=5,
)
db.add(p)
db.commit()
print(p.id, type(p.id))   # строка UUID

# Проверка CHECK
try:
    bad = ProductModel(name="Bad", price=Decimal("0"), stock=5)
    db.add(bad)
    db.commit()
except IntegrityError as e:
    print("CHECK сработал:", e)