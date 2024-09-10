from logging import getLogger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import CreateOrder, ShowOrder, UpdateOrder, DeleteOrderResponse, UpdatedOrderResponse
from db.dals import OrderDAL
from db.session import get_db

logger = getLogger(__name__)

order_router = APIRouter()

async def _create_new_order(body: CreateOrder, db: AsyncSession) -> ShowOrder:
    async with db as session:
        async with session.begin():
            order_dal = OrderDAL(session)
            order = await order_dal.create_order(
                user_id=body.user_id,
                product_id=body.product_id,
                quantity=body.quantity,
                total_price=body.total_price,
                description=body.description
            )
            return ShowOrder(
                order_id=order.order_id,
                product_id=order.product_id,
                quantity=order.quantity,
                total_price=order.total_price,
                description=order.description,
                order_status=order.order_status,
                user=order.user 
            )
        
async def _delete_order(order_id: UUID, db: AsyncSession) -> UUID | None:
    async with db as session:
        async with session.begin():
            order_dal = OrderDAL(session)
            delete_order_id = await order_dal.delete_order(order_id)
            return delete_order_id
        
async def _update_order(updated_order_params: dict, order_id: UUID, db: AsyncSession) -> UUID | None:
    async with db as session:
        async with session.begin():
            order_dal = OrderDAL(session)
            updated_order_id = await order_dal.update_order(
                order_id=order_id, **updated_order_params
            )
            return updated_order_id
        
async def _get_order_by_id(order_id: UUID, db: AsyncSession) -> ShowOrder | None:
    async with db as session:
        async with session.begin():
            order_dal = OrderDAL(session)
            order = await order_dal.get_order_by_id(order_id)
            if order is not None:
                return ShowOrder(
                    order_id=order.order_id,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    total_price=order.total_price,
                    description=order.description,
                    order_status=order.order_status,
                    user=order.user
                )

async def _get_all_orders(db: AsyncSession) -> list[ShowOrder]:
    async with db as session:
        async with session.begin():
            order_dal = OrderDAL(session)
            orders = await order_dal.get_all_orders()
            return [ShowOrder(
                order_id=order.order_id,
                product_id=order.product_id,
                quantity=order.quantity,
                total_price=order.total_price,
                description=order.description,
                order_status=order.order_status,
                user=order.user 
            ) for order in orders]
        
@order_router.post("/", response_model=ShowOrder)
async def create_order(body: CreateOrder, db: AsyncSession = Depends(get_db)) -> ShowOrder:
    try:
        return await _create_new_order(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

@order_router.delete("/", response_model=DeleteOrderResponse)
async def delete_order(order_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteOrderResponse:
    deleted_order_id = await _delete_order(order_id, db)
    if deleted_order_id is None:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
    return DeleteOrderResponse(deleted_order_id=deleted_order_id)

@order_router.get("/", response_model=ShowOrder)
async def get_order_by_id(order_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowOrder:
    order = await _get_order_by_id(order_id, db)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
    return order

# Роутер для демонстрації всіх замовлень
@order_router.get("/all", response_model=list[ShowOrder])
async def get_all_orders(db: AsyncSession = Depends(get_db)) -> list[ShowOrder]:
    return await _get_all_orders(db)

@order_router.patch("/", response_model=UpdatedOrderResponse)
async def update_order_by_id(
    order_id: UUID, body: UpdateOrder, db: AsyncSession = Depends(get_db)
) -> UpdatedOrderResponse:
    updated_order_params = body.dict(exclude_none=True)
    if updated_order_params == {}:
        raise HTTPException(
            status_code=422, 
            detail="At least one parameter for order update info should be provided"
        )
    order = await _get_order_by_id(order_id, db)
    if order is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Order with id {order_id} not found."
        )
    try:
        updated_order_id = await _update_order(
            updated_order_params=updated_order_params, db=db, order_id=order_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedOrderResponse(updated_order_id=updated_order_id)
