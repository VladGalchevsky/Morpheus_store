from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from db.models import Product
from enums import ProductStatusEnum  


class ProductDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_product(self, 
                             name: str, 
                             description: str, 
                             price: float, 
                             stock_quantity: int) -> Product:
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        self.db_session.add(new_product)
        await self.db_session.flush()
        return new_product
    
    async def delete_product(self, product_id: UUID) -> UUID | None:
        query = (
            update(Product)
            .where(and_(Product.product_id == product_id, Product.product_status != ProductStatusEnum.DELETED))
            .values(product_status=ProductStatusEnum.DELETED)
            .returning(Product.product_id)
        )
        res = await self.db_session.execute(query)
        deleted_product_id_row = res.fetchone()
        if deleted_product_id_row is not None:
            return deleted_product_id_row[0]

    async def update_product(self, product_id: UUID, **kwargs) -> UUID | None:
        query = (update(Product).where(Product.product_id == product_id).
                 values(**kwargs).returning(Product.product_id))
        res = await self.db_session.execute(query)
        updated_product_row = res.fetchone()
        if updated_product_row:
            return updated_product_row[0]

    async def get_product_by_id(self, product_id: UUID) -> Product | None:
        query = select(Product).where(Product.product_id == product_id)
        res = await self.db_session.execute(query)
        product = res.scalars().first()
        return product

    async def get_all_products(self) -> list[Product]:
        query = select(Product)
        res = await self.db_session.execute(query)
        return res.scalars().all()
    
    async def update_stock(self, product_id: UUID, quantity_change: int):
        # Checking that the number is not less than 0
        query = (update(Product).where(
                Product.product_id == product_id,
                Product.stock_quantity + quantity_change >= 0 
            )
            .values(stock_quantity=Product.stock_quantity + quantity_change)
            .execution_option(synchronize_session="fetch")
            .returning(Product.stock_quantity) 
        )

        try:
            res = await self.db_session.execute(query)
            updated_stock_row = res.fetchone()
            if updated_stock_row:
                return updated_stock_row[0]
            else:
                return None 
        except IntegrityError as e:
            return e 