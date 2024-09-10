from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    DELETED = "DELETED"