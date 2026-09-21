"""
Скрипт проверки Cart на уровне БД.

Проверяет все три уровня защиты:
1. Сохранение Cart с items (несколько позиций)
2. UNIQUE carts.user_id
3. UNIQUE cart_items (cart_id, product_id)
4. CHECK cart_items.quantity > 0
5. CHECK cart_items.price_at_added > 0
6. FK cart_items.cart_id
7. FK cart_items.product_id
8. CASCADE delete cart -> cart_items

Каждая проверка изолирована через rollback.
Каскад проверяется через raw SQL, чтобы обойти ORM-кэш.
"""
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models.product import ProductModel
from app.db.models.cart import CartModel, CartItemModel


def separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    db = SessionLocal()

    # ============================================================
    # SETUP: создаём ДВА Product, чтобы использовать их в FK product_id
    # ============================================================
    separator("SETUP: создание двух Product")

    product1 = ProductModel(
        name="Cart Test Product 1",
        price=Decimal("100.50"),
        stock=100,
    )
    product2 = ProductModel(
        name="Cart Test Product 2",
        price=Decimal("50.00"),
        stock=50,
    )
    db.add(product1)
    db.add(product2)
    db.commit()
    db.refresh(product1)
    db.refresh(product2)

    print(f"✓ Product1 создан: id={product1.id}")
    print(f"✓ Product2 создан: id={product2.id}")

    # ============================================================
    # ПРОВЕРКА 1: сохранение Cart с несколькими items
    # ============================================================
    separator("1. Сохранение Cart с items")

    cart = CartModel(user_id=str(uuid4()))
    cart.items = [
        CartItemModel(
            product_id=str(product1.id),
            quantity=2,
            price_at_added=Decimal("100.50"),
        ),
        CartItemModel(
            product_id=str(product2.id),
            quantity=1,
            price_at_added=Decimal("50.00"),
        ),
    ]
    db.add(cart)
    db.commit()
    db.refresh(cart)

    print(f"✓ Cart создан: id={cart.id}, items={len(cart.items)}")

    # ============================================================
    # ПРОВЕРКА 2: UNIQUE на carts.user_id
    # ============================================================
    separator("2. UNIQUE carts.user_id")

    try:
        duplicate = CartModel(user_id=cart.user_id)  # тот же user_id
        db.add(duplicate)
        db.commit()
        print("✗ ОШИБКА: UNIQUE не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ UNIQUE сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 3: UNIQUE на (cart_id, product_id)
    # ============================================================
    separator("3. UNIQUE (cart_id, product_id)")

    try:
        duplicate_item = CartItemModel(
            cart_id=str(cart.id),
            product_id=str(product1.id),  # уже есть в этой корзине
            quantity=1,
            price_at_added=Decimal("100.50"),
        )
        db.add(duplicate_item)
        db.commit()
        print("✗ ОШИБКА: UNIQUE (cart_id, product_id) не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ UNIQUE сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 4: CHECK quantity > 0
    # ============================================================
    # Создаём отдельную корзину, чтобы UNIQUE (cart_id, product_id) не сработал раньше
    separator("4. CHECK cart_items.quantity > 0")

    check_cart = CartModel(user_id=str(uuid4()))
    db.add(check_cart)
    db.commit()
    db.refresh(check_cart)

    try:
        bad_quantity = CartItemModel(
            cart_id=str(check_cart.id),
            product_id=str(product1.id),
            quantity=0,  # невалидно
            price_at_added=Decimal("100"),
        )
        db.add(bad_quantity)
        db.commit()
        print("✗ ОШИБКА: CHECK quantity не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ CHECK сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 5: CHECK price_at_added > 0
    # ============================================================
    separator("5. CHECK cart_items.price_at_added > 0")

    try:
        bad_price = CartItemModel(
            cart_id=str(check_cart.id),
            product_id=str(product1.id),
            quantity=1,
            price_at_added=Decimal("0"),  # невалидно
        )
        db.add(bad_price)
        db.commit()
        print("✗ ОШИБКА: CHECK price_at_added не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ CHECK сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 6: FK cart_id
    # ============================================================
    separator("6. FK cart_items.cart_id")

    try:
        bad_fk = CartItemModel(
            cart_id=str(uuid4()),  # несуществующая корзина
            product_id=str(product1.id),
            quantity=1,
            price_at_added=Decimal("100"),
        )
        db.add(bad_fk)
        db.commit()
        print("✗ ОШИБКА: FK cart_id не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ FK сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 7: FK product_id
    # ============================================================
    separator("7. FK cart_items.product_id")

    try:
        bad_product_fk = CartItemModel(
            cart_id=str(check_cart.id),
            product_id=str(uuid4()),  # несуществующий продукт
            quantity=1,
            price_at_added=Decimal("100"),
        )
        db.add(bad_product_fk)
        db.commit()
        print("✗ ОШИБКА: FK product_id не сработал!")
    except IntegrityError as e:
        db.rollback()
        print(f"✓ FK сработал: {type(e).__name__}")

    # ============================================================
    # ПРОВЕРКА 8: CASCADE delete cart -> cart_items
    # ============================================================
    separator("8. CASCADE delete cart -> cart_items")

    # Отдельная корзина с items
    cascade_cart = CartModel(user_id=str(uuid4()))
    cascade_cart.items = [
        CartItemModel(
            product_id=str(product1.id),
            quantity=5,
            price_at_added=Decimal("100"),
        ),
    ]
    db.add(cascade_cart)
    db.commit()
    db.refresh(cascade_cart)

    cascade_cart_id = cascade_cart.id

    # Считаем items через SQL (не ORM), чтобы обойти кэш
    count_before = db.execute(
        text("SELECT COUNT(*) FROM cart_items WHERE cart_id = :cid"),
        {"cid": str(cascade_cart_id)},
    ).scalar()
    print(f"  Items до удаления: {count_before}")

    # Удаляем корзину
    db.delete(cascade_cart)
    db.commit()

    # Считаем items после
    count_after = db.execute(
        text("SELECT COUNT(*) FROM cart_items WHERE cart_id = :cid"),
        {"cid": str(cascade_cart_id)},
    ).scalar()
    print(f"  Items после удаления: {count_after}")

    if count_after == 0:
        print("✓ CASCADE сработал: items удалились автоматически")
    else:
        print(f"✗ ОШИБКА: items остались! count={count_after}")

        # ============================================================
    # CLEANUP
    # ============================================================
    separator("CLEANUP")

    # 1. Сначала корзины — их items уйдут через cascade
    db.delete(cart)
    db.delete(check_cart)
    db.commit()
    print("✓ Корзины удалены (items — через cascade)")

    # 2. Потом продукты — на них больше нет ссылок
    db.delete(product1)
    db.delete(product2)
    db.commit()
    print("✓ Продукты удалены")

    db.close()
    separator("ГОТОВО")


if __name__ == "__main__":
    main()