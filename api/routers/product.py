from logging import getLogger
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from api.handlers.product import (
    _create_new_product,
    _delete_product,
    _get_all_products,
    _get_product_by_id,
    _update_product,
)
from api.models.product import (
    CreateProduct,
    ShowProduct,
    UpdateProduct,
    DeleteProductResponse,
    UpdatedProductResponse,
)
from db.dals.product_dal import ProductDAL
from dependencies.dals import get_product_dal

logger = getLogger(__name__)

product_router = APIRouter()


@product_router.post("/", response_model=ShowProduct)
async def create_product(
    body: CreateProduct, product_dal: Annotated[ProductDAL, Depends(get_product_dal)]
) -> ShowProduct:
    try:
        return await _create_new_product(body, product_dal)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@product_router.delete("/{product_id}", response_model=DeleteProductResponse)
async def delete_product(
    product_id: UUID, product_dal: Annotated[ProductDAL, Depends(get_product_dal)]
) -> DeleteProductResponse:
    deleted_product_id = await _delete_product(product_id, product_dal)
    if deleted_product_id is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found."
        )
    return DeleteProductResponse(deleted_product_id=deleted_product_id)


@product_router.get("/{product_id}", response_model=ShowProduct)
async def get_product_by_id(
    product_id: UUID, product_dal: Annotated[ProductDAL, Depends(get_product_dal)]
) -> ShowProduct:
    product = await _get_product_by_id(product_id, product_dal)
    if product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found."
        )
    return product


@product_router.get("/", response_model=list[ShowProduct])
async def get_all_products(
    product_dal: Annotated[ProductDAL, Depends(get_product_dal)],
) -> list[ShowProduct]:
    return await _get_all_products(product_dal)


@product_router.patch("/{product_id}", response_model=UpdatedProductResponse)
async def update_product_by_id(
    product_id: UUID,
    body: UpdateProduct,
    product_dal: Annotated[ProductDAL, Depends(get_product_dal)],
) -> UpdatedProductResponse:
    updated_product_params = body.dict(exclude_none=True)
    product = await _get_product_by_id(product_id, product_dal)
    if product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found."
        )
    try:
        updated_product_id = await _update_product(
            updated_product_params=updated_product_params,
            product_dal=product_dal,
            product_id=product_id,
        )
        if updated_product_id is None:
            raise HTTPException(
                status_code=404, detail=f"Product with id {product_id} not found."
            )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedProductResponse(updated_product_id=updated_product_id)
