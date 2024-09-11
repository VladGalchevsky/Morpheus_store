from enum import StrEnum


class OrderStatusEnum(StrEnum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    DELETED = "DELETED"