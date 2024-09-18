from typing import Annotated, Union

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

import settings
from db.dals.user_dal import UserDAL
from db.models import User
from hashing import Hasher
from dependencies.dals import get_user_dal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

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
