from uuid import UUID
from pydantic import BaseModel, Field


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""
        form_attribute = True


class CreateProduct(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    price: float = Field(..., gt=0.0)
    stock_quantity: int 


class ShowProduct(TunedModel):
    product_id: UUID
    name: str
    description: str | None = None
    price: float
    stock_quantity: int 


class UpdateProduct(TunedModel):
    name: str | None = Field(default=None, min_length=1, 
                             description="Optional updated name for the product")
    description: str | None = Field(default=None, min_length=1, 
                                    description="Optional updated description")
    price: float | None = Field(default=None, gt=0, 
                                description="Optional updated price, must be greater than 0")
    stock_quantity: int | None = Field(default=None, ge=0, 
                                       description="Optional updated stock quantity, must be at least 0")


class DeleteProductResponse(BaseModel):
    deleted_product_id: UUID


class UpdatedProductResponse(BaseModel):
    updated_product_id: UUID



