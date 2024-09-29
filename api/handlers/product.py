from uuid import UUID

from api.models.product import CreateProduct, ShowProduct
from db.dals.product_dal import ProductDAL


async def _create_new_product(
    body: CreateProduct, product_dal: ProductDAL
) -> ShowProduct:
    product = await product_dal.create_product(
        name=body.name,
        description=body.description,
        price=body.price,
        stock_quantity=body.stock_quantity,
    )
    return ShowProduct(
        product_id=product.product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
    )


async def _delete_product(product_id: UUID, product_dal: ProductDAL) -> UUID | None:
    delete_product_id = await product_dal.delete_product(product_id)
    return delete_product_id


async def _update_product(
    updated_product_params: dict, product_id: UUID, product_dal: ProductDAL
) -> UUID | None:
    updated_product_id = await product_dal.update_product(
        product_id=product_id, **updated_product_params
    )
    return updated_product_id


async def _get_product_by_id(
    product_id: UUID, product_dal: ProductDAL
) -> ShowProduct | None:
    product = await product_dal.get_product_by_id(product_id)
    if product is not None:
        return ShowProduct(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
        )


async def _get_all_products(product_dal: ProductDAL) -> list[ShowProduct]:
    products = await product_dal.get_all_products()
    return [
        ShowProduct(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
        )
        for product in products
    ]
