from typing import Annotated

from fastapi import Depends
from db.dals.order_dal import OrderDAL
from db.dals.product_dal import ProductDAL
from db.dals.user_dal import UserDAL
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_order_dal(db_session: Annotated[AsyncSession, Depends(get_db)]) -> OrderDAL:
    return OrderDAL(db_session=db_session)

async def get_product_dal(db_session: Annotated[AsyncSession, Depends(get_db)]) -> ProductDAL:
    return ProductDAL(db_session=db_session)

async def get_user_dal(db_session: Annotated[AsyncSession, Depends(get_db)]) -> UserDAL:
    return UserDAL(db_session=db_session)
