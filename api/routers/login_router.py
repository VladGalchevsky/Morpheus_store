from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.handlers.login_handler import authenticate_user, get_current_user_from_token
import settings
from api.models.user import Token
from db.dals.user_dal import UserDAL
from db.models import User
from security import create_access_token
from dependencies.dals import get_user_dal

login_router = APIRouter()


@login_router.post("/token", response_model=Token)
async def login_for_access_token(user_dal: Annotated[UserDAL, Depends(get_user_dal)],
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password, user_dal)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}