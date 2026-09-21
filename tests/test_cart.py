import pytest
from uuid import uuid4
from decimal import Decimal
from app.domain.cart import Cart, CartItem, ProductNotInCartError


# ============================================================
# CartItem
# ============================================================

def test_cart_item_valid_creation():
    item_id = uuid4()
    product_id = uuid4()
    item = CartItem(item_id, 2, product_id, Decimal("100.50"))

    assert item.id == item_id
    assert item.product_id == product_id
    assert item.quantity == 2
    assert item.price_at_added == Decimal("100.50")
    assert isinstance(item.price_at_added, Decimal)


@pytest.mark.parametrize("invalid_id", [None, "not-a-uuid", 123])
def test_cart_item_with_invalid_id_raises_error(invalid_id):
    with pytest.raises(ValueError):
        CartItem(invalid_id, 1, uuid4(), Decimal("100"))


def test_cart_item_with_none_product_id_raises_error():
    with pytest.raises(ValueError):
        CartItem(uuid4(), 1, None, Decimal("100"))


@pytest.mark.parametrize("invalid_quantity", [0, -1, -100])
def test_cart_item_with_invalid_quantity_raises_error(invalid_quantity):
    with pytest.raises(ValueError):
        CartItem(uuid4(), invalid_quantity, uuid4(), Decimal("100"))


@pytest.mark.parametrize("invalid_price", [
    Decimal("0"),
    Decimal("-1"),
    Decimal("-0.01"),
    100,
    100.5,
    "100",
    None,
])
def test_cart_item_with_invalid_price_raises_error(invalid_price):
    with pytest.raises(ValueError):
        CartItem(uuid4(), 1, uuid4(), invalid_price)


# ============================================================
# Cart — создание
# ============================================================

def test_cart_with_empty_items_is_valid():
    cart = Cart(uuid4(), uuid4())

    assert cart.items == []
    assert len(cart) == 0
    assert cart.total == Decimal("0")


def test_cart_with_items():
    item1 = CartItem(uuid4(), 2, uuid4(), Decimal("100"))
    item2 = CartItem(uuid4(), 1, uuid4(), Decimal("50"))
    cart = Cart(uuid4(), uuid4(), [item1, item2])

    assert len(cart) == 2
    assert cart.items[0] is item1
    assert cart.items[1] is item2


@pytest.mark.parametrize("invalid_id", [None, "abc", 123])
def test_cart_with_invalid_id_raises_error(invalid_id):
    with pytest.raises(ValueError):
        Cart(invalid_id, uuid4())


def test_cart_with_none_user_id_raises_error():
    with pytest.raises(ValueError):
        Cart(uuid4(), None)


# ============================================================
# Cart.add
# ============================================================

def test_add_new_item_to_empty_cart():
    cart = Cart(uuid4(), uuid4())
    product_id = uuid4()

    cart.add(product_id, 3, Decimal("100"))

    assert len(cart) == 1
    assert cart.items[0].product_id == product_id
    assert cart.items[0].quantity == 3
    assert cart.items[0].price_at_added == Decimal("100")


def test_add_existing_item_increments_quantity():
    """
    КЛЮЧЕВОЙ ТЕСТ. Ловит баг `item.quantity += 1`.
    Пользователь добавил 2, потом 3 → должно быть 5, а не 3.
    """
    cart = Cart(uuid4(), uuid4())
    product_id = uuid4()

    cart.add(product_id, 2, Decimal("100"))
    cart.add(product_id, 3, Decimal("100"))

    assert len(cart) == 1
    assert cart.items[0].quantity == 5


def test_add_multiple_different_items():
    cart = Cart(uuid4(), uuid4())
    product_id_1 = uuid4()
    product_id_2 = uuid4()

    cart.add(product_id_1, 2, Decimal("100"))
    cart.add(product_id_2, 1, Decimal("50"))

    assert len(cart) == 2
    assert {item.product_id for item in cart.items} == {product_id_1, product_id_2}


@pytest.mark.parametrize("invalid_quantity", [0, -1])
def test_add_item_with_invalid_quantity_raises_error(invalid_quantity):
    cart = Cart(uuid4(), uuid4())
    with pytest.raises(ValueError):
        cart.add(uuid4(), invalid_quantity, Decimal("100"))


@pytest.mark.parametrize("invalid_price", [Decimal("0"), Decimal("-1"), 100, None])
def test_add_item_with_invalid_price_raises_error(invalid_price):
    cart = Cart(uuid4(), uuid4())
    with pytest.raises(ValueError):
        cart.add(uuid4(), 1, invalid_price)


# ============================================================
# Cart.remove_item
# ============================================================

def test_remove_existing_item():
    cart = Cart(uuid4(), uuid4())
    product_id = uuid4()
    cart.add(product_id, 2, Decimal("100"))

    cart.remove_item(product_id)

    assert len(cart) == 0
    assert cart.items == []


def test_remove_nonexistent_item_raises_error():
    cart = Cart(uuid4(), uuid4())
    with pytest.raises(ProductNotInCartError):
        cart.remove_item(uuid4())


def test_remove_from_empty_cart_raises_error():
    cart = Cart(uuid4(), uuid4())
    with pytest.raises(ProductNotInCartError):
        cart.remove_item(uuid4())


def test_remove_one_of_multiple_items():
    cart = Cart(uuid4(), uuid4())
    product_id_1 = uuid4()
    product_id_2 = uuid4()
    cart.add(product_id_1, 2, Decimal("100"))
    cart.add(product_id_2, 1, Decimal("50"))

    cart.remove_item(product_id_1)

    assert len(cart) == 1
    assert cart.items[0].product_id == product_id_2


# ============================================================
# Cart.total
# ============================================================

def test_total_empty_cart_is_zero():
    cart = Cart(uuid4(), uuid4())
    assert cart.total == Decimal("0")
    assert isinstance(cart.total, Decimal)


def test_total_single_item():
    cart = Cart(uuid4(), uuid4())
    cart.add(uuid4(), 2, Decimal("100.50"))
    assert cart.total == Decimal("201.00")


def test_total_multiple_items():
    cart = Cart(uuid4(), uuid4())
    cart.add(uuid4(), 2, Decimal("100"))
    cart.add(uuid4(), 3, Decimal("50"))
    # 2*100 + 3*50 = 200 + 150 = 350
    assert cart.total == Decimal("350")


def test_total_returns_decimal_not_float():
    cart = Cart(uuid4(), uuid4())
    cart.add(uuid4(), 3, Decimal("33.33"))
    # 3 * 33.33 = 99.99
    assert cart.total == Decimal("99.99")
    assert isinstance(cart.total, Decimal)


# ============================================================
# Cart.__len__
# ============================================================

def test_len_empty():
    cart = Cart(uuid4(), uuid4())
    assert len(cart) == 0


def test_len_with_items():
    cart = Cart(uuid4(), uuid4())
    cart.add(uuid4(), 1, Decimal("10"))
    cart.add(uuid4(), 1, Decimal("20"))
    cart.add(uuid4(), 1, Decimal("30"))
    assert len(cart) == 3