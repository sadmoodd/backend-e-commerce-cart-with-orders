from uuid import UUID

from app.domain.cart import Cart
from app.domain.exceptions import ProductNotInCartError
from app.db.repositories.cart_repo import CartRepository
from app.db.repositories.product_repo import ProductRepository


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def get_cart(self, user_id: UUID) -> Cart:
        return self.cart_repo.get_or_create(user_id)

    def add_item(self, user_id: UUID, product_id: UUID, quantity: int) -> Cart:
        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ValueError("Товар не найден")

        cart = self.cart_repo.get_or_create(user_id)
        cart.add(product_id, quantity, product.price)
        self.cart_repo.save(cart)
        return cart

    def remove_item(self, user_id: UUID, product_id: UUID) -> Cart:
        cart = self.cart_repo.get_or_create(user_id)
        cart.remove_item(product_id)
        self.cart_repo.save(cart)
        return cart