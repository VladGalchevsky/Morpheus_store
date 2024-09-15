from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlalchemy import and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import User, Order
from api.models import ShowUser, ShowOrder
from enums import OrderStatusEnum


# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #

class UserDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
    
    async def delete_user(self, user_id: UUID) -> UUID | None:
        query = update(User).\
            where(and_(User.user_id == user_id, User.is_active == True)).\
            values(is_active=False).returning(User.user_id)
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id_with_orders(self, user_id: UUID) -> ShowUser | None:
        query_user = (select(User).where(User.user_id == user_id))
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
                Order.user_id == user_id, 
                Order.order_status != OrderStatusEnum.DELETED
            )
        )
        res_orders = await self.db_session.execute(query_orders)
        result_orders = res_orders.first()

        total_orders = result_orders.total_orders or 0
        total_amount = result_orders.total_amount or 0.0

        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
            total_orders=total_orders,
            total_amount=total_amount
        )
                                          
    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> UUID | None:
        query = update(User). \
            where(and_(User.user_id == user_id, User.is_active == True)). \
            values(kwargs). \
            returning(User.user_id)
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]
        

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

    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        query = select(Order).options(joinedload(Order.user)).where(Order.order_id == order_id)
        res = await self.db_session.execute(query)
        order_row = res.fetchone()
        if order_row is not None:
            return order_row[0]
    
    async def get_all_orders(self) -> list[Order]:
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
