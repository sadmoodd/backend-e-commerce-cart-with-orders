from dataclasses import dataclass, field
from uuid import UUID, uuid4
from decimal import Decimal

class ProductNotInCartError(ValueError):
    pass

@dataclass
class CartItem:
    id: UUID
    quantity: int
    product_id: UUID
    price_at_added: Decimal
    
    def __post_init__(self):
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("Неправильный id")
        if self.product_id is None:
            raise ValueError("Ошибка product_id")
        if not self.quantity >= 1:
            raise ValueError("Нельзя хранить в корзине меньше 1 ед. ытовара")
        if not isinstance(self.price_at_added, Decimal):
            raise ValueError("price_at_added must be Decimal")
        if self.price_at_added <= 0:
            raise ValueError("price_at_added must be positive")

@dataclass
class Cart:
    id: UUID
    user_id: UUID
    items: list[CartItem] = field(default_factory=list)

    
    def __post_init__(self):
        if self.id is None or not isinstance(self.id, UUID):
            raise ValueError("Неправильный id")
        if self.user_id is None:
            raise ValueError("Ошибка user_id")
        

    
    @property
    def total(self) -> Decimal:
        return sum([(item.price_at_added * item.quantity) for item in self.items], Decimal('0'))
    
    def add(self, product_id: UUID, quantity: int, price: Decimal) -> None:
        for item in self.items:
            if product_id == item.product_id:
                item.quantity += quantity
                return            
        self.items.append(CartItem(uuid4(), quantity, product_id, price))
        
    def remove_item(self, product_id: UUID) -> None:
        for i in range(len(self.items)) :
            if product_id == self.items[i].product_id:
                del self.items[i]
                return 
        raise ProductNotInCartError("Товар с таким id не найден")

    def __len__(self) -> int:
        return len(self.items)

