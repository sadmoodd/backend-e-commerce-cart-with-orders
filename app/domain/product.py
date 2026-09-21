from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal

@dataclass
class Product:
    id: UUID
    name: str 
    price: Decimal
    stock: int

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Имя не может быть пустым.")
        if self.price <= 0:
            raise ValueError("Цена должна быть положительной и больше нуля.")
        if self.stock < 0:
            raise ValueError("Нельзя создать продукт с отрицательным" \
            " остатком")
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("Неправильный id")
        if not isinstance(self.price,Decimal):
            raise ValueError("Неправильный формат цены")