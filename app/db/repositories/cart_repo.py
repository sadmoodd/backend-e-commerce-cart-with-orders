from uuid import UUID, uuid4
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.domain.cart import Cart, CartItem
from app.db.models.cart import CartModel, CartItemModel


class CartRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: CartModel) -> Cart:
        items = [
            CartItem(
                id=UUID(item.id),
                quantity=item.quantity,
                product_id=UUID(item.product_id),
                price_at_added=item.price_at_added,
            )
            for item in model.items
        ]
        return Cart(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            items=items,
        )

    def _to_model(self, domain: Cart) -> CartModel:
        model = CartModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
        )
        model.items = [
            CartItemModel(
                id=str(item.id),
                cart_id=str(domain.id),
                product_id=str(item.product_id),
                quantity=item.quantity,
                price_at_added=item.price_at_added,
            )
            for item in domain.items
        ]
        return model

    # CRUD
    def get_by_user_id(self, user_id: UUID) -> Cart | None:
        stmt = select(CartModel).where(CartModel.user_id == str(user_id))
        model = self.session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def get_or_create(self, user_id: UUID) -> Cart:
        existing = self.get_by_user_id(user_id)
        if existing is not None:
            return existing

        new_cart = Cart(
            id=uuid4(),
            user_id=user_id,
            items=[],
        )
        self.save(new_cart)
        return new_cart

    def save(self, cart: Cart) -> None:
        existing = self.session.get(CartModel, str(cart.id))

        if existing is None:
            # Новая корзина — вставляем как есть
            model = self._to_model(cart)
            self.session.add(model)
        else:
            # Существующая — синхронизируем через ORM
            existing.user_id = str(cart.user_id)

            # 1. Удалить items, которых больше нет в домене
            domain_item_ids = {str(item.id) for item in cart.items}
            for db_item in list(existing.items):
                if db_item.id not in domain_item_ids:
                    self.session.delete(db_item)

            # 2. Обновить существующие или добавить новые
            db_items_by_id = {item.id: item for item in existing.items}
            for domain_item in cart.items:
                item_id = str(domain_item.id)
                if item_id in db_items_by_id:
                    # обновляем
                    db_item = db_items_by_id[item_id]
                    db_item.quantity = domain_item.quantity
                    db_item.price_at_added = domain_item.price_at_added
                    db_item.product_id = str(domain_item.product_id)
                else:
                    # добавляем
                    self.session.add(CartItemModel(
                        id=item_id,
                        cart_id=str(cart.id),
                        product_id=str(domain_item.product_id),
                        quantity=domain_item.quantity,
                        price_at_added=domain_item.price_at_added,
                    ))

        self.session.commit()

    def delete(self, cart_id: UUID) -> None:
        model = self.session.get(CartModel, str(cart_id))
        if model is None:
            return
        self.session.delete(model)
        self.session.commit()