from logging import getLogger
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from api.handlers.order_handlers import _create_new_order, _delete_order, _get_all_orders, \
    _get_order_by_id, _update_order
from api.models.order import CreateOrder, ShowOrder, UpdateOrder, DeleteOrderResponse, UpdatedOrderResponse
from api.models.user import ShowUser
from db.dals.order_dal import OrderDAL
from db.dals.product_dal import ProductDAL
from enums import OrderStatusEnum
from dependencies.dals import get_order_dal, get_product_dal

logger = getLogger(__name__)

order_router = APIRouter()


@order_router.post("/", response_model=ShowOrder)
async def create_order(body: CreateOrder, 
                       order_dal: Annotated[OrderDAL, Depends(get_order_dal)],
                       product_dal: Annotated[ProductDAL, Depends(get_product_dal)]) -> ShowOrder:
    try:
        return await _create_new_order(body, order_dal, product_dal)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

@order_router.delete("/{order_id}", response_model=DeleteOrderResponse)
async def delete_order(order_id: UUID, order_dal: Annotated[OrderDAL, Depends(get_order_dal)]) -> DeleteOrderResponse:
    deleted_order_id = await _delete_order(order_id, order_dal)
    if deleted_order_id is None:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
    return DeleteOrderResponse(deleted_order_id=deleted_order_id)

@order_router.get("/{order_id}", response_model=ShowOrder)
async def get_order_by_id(order_id: UUID, order_dal: Annotated[OrderDAL, Depends(get_order_dal)]) -> ShowOrder:
    order = await _get_order_by_id(order_id, order_dal)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
    return order

# Router for displaying all orders
@order_router.get("/", response_model=list[ShowOrder])
async def get_all_orders(order_dal: Annotated[OrderDAL, Depends(get_order_dal)]) -> list[ShowOrder]:
    return await _get_all_orders(order_dal)

@order_router.patch("/{order_id}", response_model=UpdatedOrderResponse)
async def update_order_by_id(order_id: UUID, 
                             body: UpdateOrder, 
                             order_dal: Annotated[OrderDAL, Depends(get_order_dal)]
                             ) -> UpdatedOrderResponse:
    updated_order_params = body.dict(exclude_none=True)
    order = await _get_order_by_id(order_id, order_dal)
    if order is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Order with id {order_id} not found."
        )
    try:
        updated_order_id = await _update_order(
            updated_order_params=updated_order_params, order_dal=order_dal, order_id=order_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedOrderResponse(updated_order_id=updated_order_id)