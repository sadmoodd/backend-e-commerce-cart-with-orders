"""
Проверка всех эндпоинтов через HTTP.

Запуск:
1. uvicorn app.main:app --reload   (в одном терминале)
2. python -m scripts.check_all_endpoints   (в другом)
"""
import sys
import requests
from uuid import uuid4
from decimal import Decimal

BASE = "http://127.0.0.1:8000"


def sep(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def check(label: str, condition: bool, extra: str = "") -> None:
    if condition:
        print(f"  ✓ {label} {extra}")
    else:
        print(f"  ✗ {label} {extra}")
        sys.exit(1)


def main():
    # ============================================================
    # 0. Проверка сервера
    # ============================================================
    sep("0. Проверка сервера")
    try:
        r = requests.get(f"{BASE}/docs", timeout=3)
        check("сервер отвечает", r.status_code == 200, f"status={r.status_code}")
    except requests.ConnectionError:
        print("✗ Сервер недоступен. Запусти uvicorn app.main:app --reload")
        sys.exit(1)

    # ============================================================
    # 1. Каталог: создание продукта
    # ============================================================
    sep("1. POST /catalog/ — создание продукта")

    r = requests.post(f"{BASE}/catalog/", json={
        "name": "Test Product",
        "price": "100.50",
        "stock": 5,
    })
    check("status 201", r.status_code == 201, f"got {r.status_code}")
    data = r.json()
    product_id = data["id"]
    check("есть id", "id" in data)
    check("name корректный", data["name"] == "Test Product")
    print(f"    product_id = {product_id}")

    # ============================================================
    # 2. Каталог: попытка создать с stock=0
    # ============================================================
    sep("2. POST /catalog/ с stock=0 — ожидаем 400")

    r = requests.post(f"{BASE}/catalog/", json={
        "name": "Bad Product",
        "price": "50",
        "stock": 0,
    })
    check("status 400", r.status_code == 400, f"got {r.status_code}")

    # ============================================================
    # 3. Каталог: список
    # ============================================================
    sep("3. GET /catalog/ — список")

    r = requests.get(f"{BASE}/catalog/")
    check("status 200", r.status_code == 200)
    products = r.json()
    check("минимум 1 продукт", len(products) >= 1, f"count={len(products)}")

    # ============================================================
    # 4. Корзина: добавить item
    # ============================================================
    sep("4. POST /cart/items — добавить в корзину")

    user_id = str(uuid4())
    r = requests.post(f"{BASE}/cart/items", json={
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 2,
    })
    check("status 200", r.status_code == 200, f"got {r.status_code}")
    cart = r.json()
    check("1 item в корзине", len(cart["items"]) == 1)
    check("quantity=2", cart["items"][0]["quantity"] == 2)
    print(f"    user_id = {user_id}")

    # ============================================================
    # 5. Корзина: получить
    # ============================================================
    sep("5. GET /cart/{user_id}")

    r = requests.get(f"{BASE}/cart/{user_id}")
    check("status 200", r.status_code == 200)
    cart = r.json()
    check("item на месте", len(cart["items"]) == 1)

    # ============================================================
    # 6. Корзина: удалить item
    # ============================================================
    sep("6. DELETE /cart/items/{user_id}/{product_id}")

    # Сначала добавим второй item, чтобы после удаления остался один
    r = requests.post(f"{BASE}/catalog/", json={
        "name": "Second Product",
        "price": "25.00",
        "stock": 10,
    })
    product_id_2 = r.json()["id"]

    r = requests.post(f"{BASE}/cart/items", json={
        "user_id": user_id,
        "product_id": product_id_2,
        "quantity": 1,
    })
    check("2 items в корзине", len(r.json()["items"]) == 2)

    r = requests.delete(f"{BASE}/cart/items/{user_id}/{product_id_2}")
    check("status 200", r.status_code == 200)
    cart = r.json()
    check("1 item остался", len(cart["items"]) == 1)

    # ============================================================
    # 7. Оплата (прямая)
    # ============================================================
    sep("7. POST /payments/")

    r = requests.post(f"{BASE}/payments/", params={
        "order_id": str(uuid4()),
        "amount": "100.50",
    })
    check("status 200", r.status_code == 200)
    data = r.json()
    check("success=True", data["success"] is True)
    check("есть transaction_id", data["transaction_id"] is not None)

    # ============================================================
    # 8. Оформление заказа
    # ============================================================
    sep("8. POST /orders/checkout")

    r = requests.post(f"{BASE}/orders/checkout", params={"user_id": user_id})
    check("status 200", r.status_code == 200, f"got {r.status_code}")
    order = r.json()
    check("status=paid", order["status"] == "paid")
    check("total > 0", float(order["total"]) > 0)
    print(f"    order_id = {order['id']}, total = {order['total']}")

    # ============================================================
    # 9. Оформление пустой корзины
    # ============================================================
    sep("9. POST /orders/checkout с пустой корзиной — ожидаем 400")

    empty_user = str(uuid4())
    r = requests.post(f"{BASE}/orders/checkout", params={"user_id": empty_user})
    check("status 400", r.status_code == 400, f"got {r.status_code}")

    # ============================================================
    sep("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    print("✓ DONE")


if __name__ == "__main__":
    main()