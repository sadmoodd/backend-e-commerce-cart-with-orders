from uuid import uuid4
from decimal import Decimal

from uuid import UUID

from app.db.session import SessionLocal
from app.db.models.product import ProductModel
from app.db.repositories.cart_repo import CartRepository
from app.domain.cart import Cart


db = SessionLocal()

# Setup: два продукта
p1 = ProductModel(name="P1", price=Decimal("100"), stock=10)
p2 = ProductModel(name="P2", price=Decimal("50"), stock=10)
db.add(p1)
db.add(p2)
db.commit()
db.refresh(p1)
db.refresh(p2)

repo = CartRepository(db)

# 1. create + save с items
user_id = uuid4()
cart = Cart(id=uuid4(), user_id=user_id, items=[])
cart.add(p1.id, 2, Decimal("100"))
cart.add(p2.id, 1, Decimal("50"))
repo.save(cart)
print(f"✓ Saved cart with {len(cart)} items")

# 2. read
loaded = repo.get_by_user_id(user_id)
print(f"✓ Loaded: items={len(loaded)}, total={loaded.total}")



# 3. update quantity
loaded.items[0].quantity = 10
repo.save(loaded)
loaded2 = repo.get_by_user_id(user_id)

print("p1.id =", p1.id)
print("p2.id =", p2.id)
print("loaded2.items:")
for i, item in enumerate(loaded2.items):
    print(f"  [{i}] product_id={item.product_id}, qty={item.quantity}")

print(f"✓ After update: qty={loaded2.items[0].quantity}")

# 4. remove item
loaded2.remove_item(UUID(p2.id))

repo.save(loaded2)
loaded3 = repo.get_by_user_id(user_id)
print(f"✓ After remove: items={len(loaded3)}")



# 5. delete cart
repo.delete(loaded3.id)
gone = repo.get_by_user_id(user_id)
print(f"✓ After delete: {gone}")




# Cleanup
db.delete(p1)
db.delete(p2)
db.commit()
db.close()
print("✓ DONE")