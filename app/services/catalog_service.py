from uuid import uuid4
from decimal import Decimal

from app.domain.product import Product
from app.domain.exceptions import CannotAddProductWithoutStock
from app.db.repositories.product_repo import ProductRepository


class CatalogService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def list_products(self) -> list[Product]:
        return self.repo.get_all()

    def get_product(self, product_id) -> Product | None:
        return self.repo.get_by_id(product_id)

    def add_product(self, name: str, price: Decimal, stock: int) -> Product:
        if stock <= 0:
            raise CannotAddProductWithoutStock("Нельзя добавить товар с нулевым остатком")
        product = Product(uuid4(), name, price, stock)
        self.repo.save(product)
        return product