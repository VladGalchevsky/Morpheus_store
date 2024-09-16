from dataclasses import dataclass


@dataclass
class UserWithOrderSummary:
    user_id: str
    name: str
    surname: str
    email: str
    is_active: bool
    total_orders: int
    total_amount: float