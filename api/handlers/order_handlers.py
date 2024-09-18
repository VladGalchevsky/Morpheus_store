from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from api.models.order import CreateOrder, ShowOrder
from api.models.user import ShowUser
from db.dals.order_dal import OrderDAL
from db.dals.product_dal import ProductDAL
from enums import OrderStatusEnum
from dependencies.dals import get_order_dal, get_product_dal
from dataclasses_ import OrderWithUserSummary

async def _create_new_order(body: CreateOrder,
                            order_dal: Annotated[OrderDAL, Depends(get_order_dal)],
                            product_dal: Annotated[ProductDAL, Depends(get_product_dal)]) -> ShowOrder:
    
    product = await product_dal.get_product_by_id(body.product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock_quantity < body.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for this product.")

    order = await order_dal.create_order(
        user_id=body.user_id,
        product_id=body.product_id,
        quantity=body.quantity,
        total_price=body.total_price,
        description=body.description
    )
    await product_dal.update_stock(body.product_id, -body.quantity)     

    return ShowOrder(
        order_id=order.order_id,
        quantity=order.quantity,
        total_price=order.total_price,
        description=order.description,
        order_status=order.order_status
    )
        
async def _delete_order(order_id: UUID, order_dal: OrderDAL, product_dal:ProductDAL) -> UUID | None:
        # Receive order data
        order = await order_dal.get_order_by_id(order_id)
        if not order or order.order_status == OrderStatusEnum.DELETED:
            return None
        # Returning the quantity of products to the warehouse
        await product_dal.update_stock(order.product_id, order.quantity)
        # Mark the order as deleted
        delete_order_id = await order_dal.delete_order(order_id)
        return delete_order_id
        
async def _update_order(updated_order_params: dict, order_id: UUID, order_dal: OrderDAL) -> UUID | None:
        updated_order_id = await order_dal.update_order(
            order_id=order_id, **updated_order_params
        )
        return updated_order_id
        
async def _get_order_by_id(order_id: UUID, order_dal: OrderDAL) -> OrderWithUserSummary | None:
        order = await order_dal.get_order_by_id(order_id=order_id)
        return order 
        
async def _get_all_orders(order_dal: OrderDAL) -> list[ShowOrder]:
        orders = await order_dal.get_all_orders()
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
                    is_active=order.user.is_active
                ) if order.user else None
            ) for order in orders
        ]
