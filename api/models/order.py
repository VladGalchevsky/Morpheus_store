import uuid

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator, root_validator
from enums import OrderStatusEnum

from api.models.user import ShowUser


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        form_attribute = True


class CreateOrder(BaseModel):
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(gt=0, description="Quantity should be greater than 0")
    total_price: float = Field(gt=0.0, description="Price must be greater than 0")
    description: str | None = None


class ShowOrder(TunedModel):
    order_id: uuid.UUID
    quantity: int
    total_price: float
    description: str | None = None
    order_status: OrderStatusEnum
    user: ShowUser | None = None


class UpdateOrder(BaseModel):
    quantity: int | None
    total_price: float | None
    description: str | None = None
    order_status: OrderStatusEnum | None

    @validator("quantity", pre=True, always=True)
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise HTTPException(
                status_code=422, detail="Quantity should be greater than 0"
            )
        return value

    @validator("total_price", pre=True, always=True)
    def validate_total_price(cls, value):
        if value is not None and value <= 0:
            raise HTTPException(
                status_code=422, detail="Total price should be greater than 0"
            )
        return value

    @root_validator(pre=True)
    def validate_non_empty_update(cls, values):
        # Raise an error if all fields are None
        if not any(values.values()):
            raise HTTPException(
                status_code=422,
                detail="At least one parameter for order update must be provided",
            )
        return values


class DeleteOrderResponse(BaseModel):
    deleted_order_id: uuid.UUID


class UpdatedOrderResponse(BaseModel):
    updated_order_id: uuid.UUID
