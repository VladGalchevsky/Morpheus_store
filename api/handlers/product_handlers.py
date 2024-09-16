from logging import getLogger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.product_models import CreateProduct, ShowProduct, UpdateProduct, DeleteProductResponse, UpdatedProductResponse
from db.dals.product_dals import ProductDAL
from db.session import get_db

logger = getLogger(__name__)

product_router = APIRouter()

async def _create_new_product(body: CreateProduct, session: AsyncSession) -> ShowProduct:
    async with session.begin():
        product_dal = ProductDAL(session)
        product = await product_dal.create_product(
            name=body.name,
            description=body.description,
            price=body.price,
            stock_quantity=body.stock_quantity
        )
        return ShowProduct(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity
        )
        
async def _delete_product(product_id: UUID, session: AsyncSession) -> UUID | None:
    async with session.begin():
        product_dal = ProductDAL(session)
        delete_product_id = await product_dal.delete_product(product_id)
        return delete_product_id
        
async def _update_product(updated_product_params: dict, product_id: UUID, session: AsyncSession) -> UUID | None:
    async with session.begin():
        product_dal = ProductDAL(session)
        updated_product_id = await product_dal.update_product(
            product_id=product_id, **updated_product_params
        )
        return updated_product_id
        
async def _get_product_by_id(product_id: UUID, session: AsyncSession) -> ShowProduct | None:
    async with session.begin():
        product_dal = ProductDAL(session)
        product = await product_dal.get_product_by_id(product_id)
        if product is not None:
            return ShowProduct(
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock_quantity=product.stock_quantity
            )

async def _get_all_products(session: AsyncSession) -> list[ShowProduct]:
    async with session.begin():
        product_dal = ProductDAL(session)
        products = await product_dal.get_all_products()
        return [
            ShowProduct(
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock_quantity=product.stock_quantity
            ) for product in products
        ]
        
@product_router.post("/", response_model=ShowProduct)
async def create_product(body: CreateProduct, db: AsyncSession = Depends(get_db)) -> ShowProduct:
    try:
        return await _create_new_product(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

@product_router.delete("/{product_id}", response_model=DeleteProductResponse)
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteProductResponse:
    deleted_product_id = await _delete_product(product_id, db)
    if deleted_product_id is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    return DeleteProductResponse(deleted_product_id=deleted_product_id)

@product_router.get("/{product_id}", response_model=ShowProduct)
async def get_product_by_id(product_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowProduct:
    product = await _get_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    return product

@product_router.get("/", response_model=list[ShowProduct])
async def get_all_products(db: AsyncSession = Depends(get_db)) -> list[ShowProduct]:
    return await _get_all_products(db)

@product_router.patch("/{product_id}", response_model=UpdatedProductResponse)
async def update_product_by_id(
    product_id: UUID, body: UpdateProduct, db: AsyncSession = Depends(get_db)) -> UpdatedProductResponse:
    updated_product_params = body.dict(exclude_none=True)
    product = await _get_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Product with id {product_id} not found."
        )
    try:
        updated_product_id = await _update_product(
            updated_product_params=updated_product_params, session=db, product_id=product_id
        )
        if updated_product_id is None:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedProductResponse(updated_product_id=updated_product_id)