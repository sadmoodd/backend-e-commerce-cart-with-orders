from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4


class CartItemModel(Base):
    __tablename__ = "cart_items"
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
        CheckConstraint("price_at_added > 0", name="ck_cart_item_price_positive"),
        UniqueConstraint("cart_id", "product_id", name="uq_cart_item_cart_product")
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_added: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    cart: Mapped["CartModel"] = relationship(back_populates="items")
    
    
class CartModel(Base):
    __tablename__ = "carts"
    
    __table_args__= (
        
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False) # нет смысла добавлять пользователей
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), 
                                                  onupdate=datetime.now(timezone.utc))
    
    items: Mapped[list["CartItemModel"]] = relationship(back_populates="cart", cascade="all, delete-orphan")
    
    