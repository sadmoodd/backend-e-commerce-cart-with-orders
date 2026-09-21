from uuid import UUID, uuid4
from app.domain.product import Product
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.db.models.product import ProductModel
from app.domain.product import Product


# TODO сделать асинхронные функции через asyncio
class ProductRepository:
    def __init__(self, session: Session):
        self.session = session
        
    def _to_domain(self, model: ProductModel) -> Product:
        return Product(UUID(model.id), model.name, model.price, model.stock)

    def _to_model(self, domain: Product) -> ProductModel:
        return ProductModel(
            id=str(domain.id), 
            name=domain.name, 
            price=domain.price, 
            stock=domain.stock)

    def get_by_id(self, product_id: UUID) -> Product | None:
        stmt = select(ProductModel).where(ProductModel.id == str(product_id))
        model = self.session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)
    
    def get_all(self) -> list[Product]:
        stmt = select(ProductModel)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]
            
    def save(self, product: Product):
        model = self._to_model(product)
        self.session.add(model)
        self.session.commit()
            
    def update_stock(self, product_id: UUID, new_stock: int) -> None:
        stmt = update(ProductModel).where(ProductModel.id == str(product_id)).values(stock=new_stock)
        self.session.execute(stmt)
        self.session.commit()
        
    def delete(self, product_id: UUID) -> None:
        stmt = delete(ProductModel).where(ProductModel.id == str(product_id))
        self.session.execute(stmt)
        self.session.commit()
    
