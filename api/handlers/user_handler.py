from logging import getLogger
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import UserCreate, ShowUser, DeleteUserResponse, \
    UpdateUserRequest, UpdatedUserResponse
from db.dals.user_dal import UserDAL, UserWithOrderSummary
from db.session import get_db
from hashing import Hasher

logger = getLogger(__name__)

user_router = APIRouter()

async def get_user_dal(db_session: Annotated[AsyncSession, Depends(get_db)]) -> UserDAL:
    return UserDAL(db_session=db_session)


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

async def _update_user(updated_user_params: dict, 
                       user_id: UUID, 
                       user_dal: UserDAL) -> UUID | None:
        updated_user_id = await user_dal.update_user(user_id=user_id, 
                                                     **updated_user_params)
        return updated_user_id

async def _get_user_by_id(user_id: UUID, 
                          user_dal: UserDAL
                          ) -> UserWithOrderSummary | None:
        user_with_orders = await user_dal.get_user_by_id_with_orders(user_id=user_id)
        return user_with_orders

@user_router.post("/", response_model=ShowUser, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, 
                      user_dal: Annotated[UserDAL, Depends(get_user_dal)]) -> ShowUser:
    try:
        return await _create_new_user(body, user_dal)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, 
                      user_dal: Annotated[UserDAL, Depends(get_user_dal)]) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, user_dal)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, 
                            detail=f"User with id {user_id} not found.")
    return DeleteUserResponse(deleted_user_id=deleted_user_id)

@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, 
                         user_dal: Annotated[UserDAL, Depends(get_user_dal)]) -> ShowUser:
    user = await _get_user_by_id(user_id, user_dal)
    if user is None:
        raise HTTPException(status_code=404, 
                            detail=f"User with id {user_id} not found.")
    return user

@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(user_id: UUID, 
                            body: UpdateUserRequest, 
                            user_dal: Annotated[UserDAL, Depends(get_user_dal)]
                            ) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=422, 
            detail="At least one parameter for user update info should be provided"
            )
    user = await _get_user_by_id(user_id, user_dal)
    if user is None:
        raise HTTPException(status_code=404, 
                            detail=f"User with id {user_id} not found.")
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, 
            user_dal=user_dal, 
            user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)