from uuid import UUID
from app.domain.product import Product

class ProductReposytory:
    def __init__(self):
        ...

    def get_by_id(product_id: UUID) -> Product | None:
        ...
