from datetime import datetime
import uuid

from sqlalchemy import DateTime, Enum, Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, INTEGER, FLOAT
from sqlalchemy.orm import declarative_base, relationship
from enums import OrderStatusEnum, ProductStatusEnum


# BLOCK WITH DATABASE MODELS #

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True, index=True)
    hashed_password = Column(String, nullable=False)
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"))
    quantity = Column(INTEGER, nullable=False)
    total_price = Column(FLOAT, nullable=False)
    description = Column(String, nullable=True)
    order_status = Column(
        Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False
    )
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="orders")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    stock_quantity = Column(INTEGER, default=0)
    price = Column(FLOAT, nullable=False)
    description = Column(String, nullable=True)
    product_status = Column(
        Enum(ProductStatusEnum), default=ProductStatusEnum.ACTIVE, nullable=False
    )
