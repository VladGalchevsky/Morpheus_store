from uuid import UUID

from api.models.user import UserCreate, ShowUser
from db.dals.user_dal import UserDAL, UserWithOrderSummary
from hashing import Hasher


async def _create_new_user(body: UserCreate, user_dal: UserDAL) -> ShowUser:
    user = await user_dal.create_user(
        name=body.name,
        surname=body.surname,
        email=body.email,
        hashed_password=Hasher.get_password_hash(body.password),
    )
    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )


async def _delete_user(user_id, user_dal: UserDAL) -> UUID | None:
    deleted_user_id = await user_dal.delete_user(user_id=user_id)
    return deleted_user_id


async def _update_user(
    updated_user_params: dict, user_id: UUID, user_dal: UserDAL
) -> UUID | None:
    updated_user_id = await user_dal.update_user(user_id=user_id, **updated_user_params)
    return updated_user_id


async def _get_user_by_id(
    user_id: UUID, user_dal: UserDAL
) -> UserWithOrderSummary | None:
    user_with_orders = await user_dal.get_user_by_id_with_orders(user_id=user_id)
    return user_with_orders
