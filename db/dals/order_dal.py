from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.models.user import ShowUser
from db.models import Order, User
from api.models.order import ShowOrder
from enums import OrderStatusEnum
from dataclasses_ import OrderWithUserSummary, UserWithOrderSummary


class OrderDAL:
    """Data Access Layer for operating order info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_order(
            self, 
            user_id: UUID,
            product_id: UUID,  
            quantity: int,
            total_price: float, 
            description: str,
        ) -> Order:
        
        new_order = Order(
            user_id=user_id,
            product_id=product_id,
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

    async def get_order_by_id(self, order_id: UUID) -> OrderWithUserSummary | None:
        query_order = select(Order).where(Order.order_id == order_id)
        res_order = await self.db_session.execute(query_order)
        order = res_order.scalars().first()

        if not order:
            return None
        
        query_user = select(User).where(User.user_id == order.user_id)
        res_user = await self.db_session.execute(query_user)
        user = res_user.scalars().first()
        
        if not user:
            return None
        
        query_orders = (
            select(
                func.count(Order.order_id).label("total_orders"),
                func.sum(Order.total_price).label("total_amount")
            )
            .where(
                Order.user_id == order.user_id,
                Order.order_status != OrderStatusEnum.DELETED
            )
        ) 
        res_orders = await self.db_session.execute(query_orders)
        result_orders = res_orders.first()
        total_orders = result_orders.total_orders or 0
        total_amount = result_orders.total_amount or 0.0

        return OrderWithUserSummary(
            order_id=str(order.order_id),
            quantity=order.quantity,
            total_price=order.total_price,
            description=order.description,
            order_status=order.order_status,
            user=UserWithOrderSummary(
                user_id=str(user.user_id),
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
                total_orders=total_orders,
                total_amount=total_amount
            )
        )

    async def get_all_orders(self) -> list[ShowOrder]:
        query = select(Order).options(joinedload(Order.user)).order_by(Order.order_date.desc())
        res = await self.db_session.execute(query)
        orders = res.scalars().all()
        return [
            ShowOrder(
                order_id=order.order_id,
                quantity=order.quantity,
                total_price=order.total_price,
                description=order.description,
                order_status=order.order_status,
                user=ShowUser(
                    user_id=order.user.user_id,
                    name=order.user.name,
                    surname=order.user.surname,
                    email=order.user.email,
                    is_active=order.user.is_active,
                ) if order.user else None
            ) for order in orders
        ]

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