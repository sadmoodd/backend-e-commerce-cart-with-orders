from app.domain.product import Product
from uuid import uuid4
from decimal import Decimal
import pytest

def test_create_valid_product():
    product_id  = uuid4()
    p = Product(product_id , "Name", Decimal("100.5"), 5)
    assert p.price == Decimal("100.5")
    assert p.name == "Name"
    assert p.stock == 5
    assert p.id == product_id 

# ===== PRICE =====
def test_product_with_negative_price():
    with pytest.raises(ValueError):
        Product(uuid4() , "Name", Decimal("-100.5"), 5)

def test_product_with_zero_price():
    with pytest.raises(ValueError):
        Product(uuid4(), "Name", Decimal("0"), 5)

def test_product_with_non_decimal_price():
    with pytest.raises(ValueError):
        Product(uuid4(),"Name", 100, 5)

# ===== STOCK =====
def test_product_with_negative_stock():
    with pytest.raises(ValueError):
        Product(uuid4(),"Name", Decimal("100"), -5)

def test_product_with_zero_stock():
    p = Product(uuid4(),"Name", Decimal("100"), 0)
    assert p.stock == 0

# ===== NAME =====
def test_product_with_empty_name():
    with pytest.raises(ValueError):
        Product(uuid4(),"", Decimal("100"), 5)

def test_product_with_space_name():
    with pytest.raises(ValueError):
        Product(uuid4(),"        ", Decimal("100"), 5)

# ===== ID =====
def test_product_with_empty_id():
    with pytest.raises(ValueError):
        empty_id = ""
        Product(empty_id,"Name", Decimal("100"), 5)

def test_product_with_none_id():
    with pytest.raises(ValueError):
        Product(None,"Name", Decimal("100"), 5)

def test_product_with_str_id():
    with pytest.raises(ValueError):
        Product("id","Name", Decimal("100"), 5)

def test_product_with_int_id():
    with pytest.raises(ValueError):
        Product(12,"Name", Decimal("100"), 5)


