import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from enums import OrderStatusEnum


# BLOCK WITH API MODELS #

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""
        orm_mode = True

# BLOCK WITH USER MODELS #

class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value
    
    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID
 

class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, examples=["Vladislav"])
    surname: str | None = Field(default=None, min_length=1, examples=["Amosov"])
    email: EmailStr | None = Field(default=None, examples=["lol@kek.com"])

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value
    
    # BLOCK WITH ORDER MODELS #

class CreateOrder(BaseModel):
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(gt=0, description="Quantity should be greater than 0")
    total_price: float = Field(gt=0.0, description="Price must be greater than 0")
    description: str | None = None

class ShowOrder(TunedModel):
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    total_price: float
    description: str | None = None
    order_status: OrderStatusEnum
    user: ShowUser 

class UpdateOrder(BaseModel):
    product_id: uuid.UUID | None
    quantity: int | None
    total_price: float | None
    description: str | None = None
    order_status: OrderStatusEnum | None

    @validator("quantity", pre=True, always=True)
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise HTTPException(status_code=422, detail="Quantity should be greater than 0")
        return value

    @validator("total_price", pre=True, always=True)
    def validate_total_price(cls, value):
        if value is not None and value <= 0:
            raise HTTPException(status_code=422, detail="Total price should be greater than 0")
        return value
    
    @root_validator(pre=True)
    def validate_non_empty_update(cls, values):
        # Raise an error if all fields are None
        if not any(values.values()):
            raise HTTPException(status_code=422, detail="At least one parameter for order update must be provided")
        return values

class DeleteOrderResponse(BaseModel):
    deleted_order_id: uuid.UUID

class UpdatedOrderResponse(BaseModel):
    updated_order_id: uuid.UUID


class Token(BaseModel):
    access_token: str
    token_type: str