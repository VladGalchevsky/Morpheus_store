from datetime import timedelta
from typing import Annotated, Union

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.models.user import Token
from db.dals.user_dal import UserDAL
from db.models import User
from db.session import get_db
from hashing import Hasher
from security import create_access_token
from api_template.dependencies.dals import get_user_dal

login_router = APIRouter()


async def _get_user_by_email_for_auth(email: str, user_dal:UserDAL):
            return await user_dal.get_user_by_email(email=email)

async def authenticate_user(email: str, password: str, user_dal:UserDAL) -> Union[User, None]:
    user = await _get_user_by_email_for_auth(email=email, user_dal=user_dal)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(user_dal: Annotated[UserDAL, Depends(get_user_dal)], 
                                      token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        print("username/email extracted is ", email)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(email=email, user_dal=user_dal)
    if user is None:
        raise credentials_exception
    return user


@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}