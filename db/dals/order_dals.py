from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlalchemy import and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import Order
from api.models.order_models import ShowOrder
from enums import OrderStatusEnum


class OrderDAL:
    """Data Access Layer for operating order info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_order(
            self, 
            user_id: UUID,  
            quantity: int,
            total_price: float, 
            description: str,
        ) -> Order:
        
        new_order = Order(
            user_id=user_id,
            quantity=quantity,
            total_price=total_price,
            description=description
        )
        self.db_session.add(new_order)
        await self.db_session.flush()
        return new_order
    
    async def delete_order(self, order_id: UUID) -> UUID | None:
        query = update(Order). \
            where(and_(Order.order_id == order_id, Order.order_status != OrderStatusEnum.DELETED)). \
            values(order_status=OrderStatusEnum.DELETED). \
            returning(Order.order_id)
        res = await self.db_session.execute(query)
        deleted_order_id_row = res.fetchone()
        if deleted_order_id_row is not None:
            return deleted_order_id_row[0]

    async def get_order_by_id(self, order_id: UUID) -> ShowOrder | None:
        query = select(Order).options(joinedload(Order.user)).where(Order.order_id == order_id)
        res = await self.db_session.execute(query)
        order_row = res.fetchone()
        if order_row is not None:
            return order_row[0]
    
    async def get_all_orders(self) -> list[ShowOrder]:
        query = select(Order).options(joinedload(Order.user)).order_by(Order.order_date.desc())
        res = await self.db_session.execute(query)
        return res.scalars().all()

    async def update_order(self, order_id: UUID, **kwargs) -> UUID | None:
        # Видалення поля order_status з kwargs якщо воно присутнє
        kwargs.pop("order_status", None)

        if not kwargs:
            raise ValueError("No fields provided for update")
        
        query = update(Order). \
            where(and_(Order.order_id == order_id, Order.order_status != OrderStatusEnum.DELETED)). \
            values(kwargs). \
            returning(Order.order_id)
        res = await self.db_session.execute(query)
        updated_order_id_row = res.fetchone()
        if updated_order_id_row is not None:
            return updated_order_id_row[0]
        
        # Change the order status only    
    async def change_order_status(self, order_id: UUID, new_status: OrderStatusEnum) -> UUID | None:
        query = update(Order). \
            where(and_(Order.order_id == order_id, Order.order_status != OrderStatusEnum.DELETED)). \
            values(order_status=new_status). \
            returning(Order.order_id)
        res = await self.db_session.execute(query)
        updated_order_id_row = res.fetchone()
        if updated_order_id_row is not None:
            return updated_order_id_row[0]