"""The FastAPI dependencies"""

import os
from typing import Annotated
from werkzeug.security import check_password_hash
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

try:
    from database.models import models
    from database.commands import session_commands
    from app.fastapi.models.fastapi_models import (
        UserModel,
        UserInDB,
        TokenData,
    )
except ModuleNotFoundError:
    from app.packages.database.models import models
    from app.packages.database.commands import session_commands
    from app.packages.fastapi.models.fastapi_models import (
        UserModel,
        UserInDB,
        TokenData,
    )


# tokenUrl leads to the URI "/api/v1/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
# session used by the FastAPI application
session = session_commands.init_and_get_a_database_session()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def get_user(username: str):
    """get user in db"""
    user = session.query(models.User).filter_by(username=username).first()
    if user:
        return UserInDB(**user.get_json())
    return None


def verify_password(plain_password, hashed_password):
    """check password hash"""
    return check_password_hash(hashed_password, plain_password)


def authenticate_user(username: str, password: str):
    """authenticate_user > returns an User instance"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """get the current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """return current user if not disabled"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user
