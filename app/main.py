from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

from app.db import models  # noqa: F401 — регистрация таблиц
from app.db.session import engine, get_db
from app.db.base import Base

from app.db.repositories.product_repo import ProductRepository
from app.db.repositories.cart_repo import CartRepository
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.domain.exceptions import (
    CannotAddProductWithoutStock,
    ProductNotInCartError,
)
from app.services.payment.facade import PaymentFacade
from app.services.payment.fake_adapter import FakePaymentAdapter

from app.domain.order import Order
from app.domain.order import OrderStatus
from app.db.repositories.order_repo import OrderRepository
from app.services.order_service import OrderService, EmptyCartError, PaymentFailedError
from app.services.payment import PaymentFacade, FakePaymentAdapter


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TPPS LR2 Shop")


# ============================================================
# Pydantic схемы (запросы/ответы)
# ============================================================

class ProductCreate(BaseModel):
    name: str
    price: Decimal
    stock: int


class ProductRead(BaseModel):
    id: UUID
    name: str
    price: Decimal
    stock: int


class CartItemRead(BaseModel):
    product_id: UUID
    quantity: int
    price_at_added: Decimal


class CartRead(BaseModel):
    id: UUID
    user_id: UUID
    items: list[CartItemRead]


class AddItemRequest(BaseModel):
    user_id: UUID
    product_id: UUID
    quantity: int

class OrderRead(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total: Decimal

# ============================================================
# Dependencies
# ============================================================

def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    return CatalogService(ProductRepository(db))


def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(CartRepository(db), ProductRepository(db))

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    payment = PaymentFacade(FakePaymentAdapter())
    return OrderService(
        cart_repo=CartRepository(db),
        order_repo=OrderRepository(db),
        payment=payment,
    )


# ============================================================
# Endpoints: Каталог
# ============================================================

@app.get("/catalog/", response_model=list[ProductRead])
def list_products(service: CatalogService = Depends(get_catalog_service)):
    products = service.list_products()
    return [
        ProductRead(id=p.id, name=p.name, price=p.price, stock=p.stock)
        for p in products
    ]


@app.post("/catalog/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def add_product(
    data: ProductCreate,
    service: CatalogService = Depends(get_catalog_service),
):
    try:
        product = service.add_product(data.name, data.price, data.stock)
    except CannotAddProductWithoutStock as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ProductRead(id=product.id, name=product.name, price=product.price, stock=product.stock)


# ============================================================
# Endpoints: Корзина
# ============================================================

@app.get("/cart/{user_id}", response_model=CartRead)
def get_cart(user_id: UUID, service: CartService = Depends(get_cart_service)):
    cart = service.get_cart(user_id)
    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemRead(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_added=item.price_at_added,
            )
            for item in cart.items
        ],
    )


@app.post("/cart/items", response_model=CartRead)
def add_item(
    data: AddItemRequest,
    service: CartService = Depends(get_cart_service),
):
    try:
        cart = service.add_item(data.user_id, data.product_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemRead(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_added=item.price_at_added,
            )
            for item in cart.items
        ],
    )


@app.delete("/cart/items/{user_id}/{product_id}", response_model=CartRead)
def remove_item(
    user_id: UUID,
    product_id: UUID,
    service: CartService = Depends(get_cart_service),
):
    try:
        cart = service.remove_item(user_id, product_id)
    except ProductNotInCartError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemRead(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_added=item.price_at_added,
            )
            for item in cart.items
        ],
    )
    
    
@app.post("/payments/")
def pay_order(order_id: UUID, amount: Decimal):
    facade = PaymentFacade(FakePaymentAdapter())
    result = facade.pay_order(order_id, amount)
    return {"success": result.success, "transaction_id": result.transaction_id}

@app.post("/orders/checkout", response_model=OrderRead)
def checkout(user_id: UUID, service: OrderService = Depends(get_order_service)):
    try:
        order = service.checkout(user_id)
    except EmptyCartError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentFailedError as e:
        raise HTTPException(status_code=402, detail=str(e))
    return OrderRead(
        id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        total=order.total,
    )