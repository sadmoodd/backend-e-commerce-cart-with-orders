from app.db.session import SessionLocal
from app.db.repositories.product_repo import ProductRepository
from app.domain.product import Product
from uuid import uuid4
from decimal import Decimal

db = SessionLocal()
repo = ProductRepository(db)

# Создать
p = Product(uuid4(), "Test", Decimal("100"), 5)
repo.save(p)

# Прочитать
found = repo.get_by_id(p.id)
print(found, type(found))

# Все
all_products = repo.get_all()
print(len(all_products))

# Обновить
repo.update_stock(p.id, 10)
updated = repo.get_by_id(p.id)
print(updated.stock)  # 10

# Удалить
repo.delete(p.id)
gone = repo.get_by_id(p.id)
print(gone)  # None

db.close()