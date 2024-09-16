from enum import StrEnum


class OrderStatusEnum(StrEnum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    DELETED = "DELETED"


class ProductStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    DELETED = "DELETED"