from datetime import datetime, timezone
from fastapi import Request, Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import redirect_or_raise
from app.auth.dao import UsersDAO
from app.models.models import User
from app.config import settings
from app.dependencies.dao_dep import get_session_without_commit

from app.exceptions import (
    TokenNoFound,
    NoJwtException,
    TokenExpiredException,
    NoUserIdException,
    ForbiddenException,
    UserNotFoundException
)


def get_access_token(request: Request):
    """Извлекаем access_token из кук. Возвращает None, если токена нет."""
    return request.cookies.get('user_access_token')


def get_refresh_token(request: Request):
    token = request.cookies.get('user_refresh_token')
    if token is None:
        redirect_or_raise(request, TokenNoFound)
    else:
        return token


async def check_refresh_token(
    request: Request,
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise NoJwtException

        user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
        if not user:
            raise NoJwtException

        return user
    except JWTError:
        redirect_or_raise(request, NoJwtException)


async def get_current_user(
    request: Request,
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        redirect_or_raise(request, TokenExpiredException)
    except JWTError:
        redirect_or_raise(request, NoJwtException)

    expire_ts = payload.get('exp')
    if expire_ts is None:
        redirect_or_raise(request, TokenExpiredException)

    expire_time = datetime.fromtimestamp(int(expire_ts), tz=timezone.utc)
    if expire_time < datetime.now(timezone.utc):
        redirect_or_raise(request, TokenExpiredException)

    user_id = payload.get('sub')
    if user_id is None:
        redirect_or_raise(request, NoUserIdException)

    user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
    if not user:
        redirect_or_raise(request, TokenNoFound)
    else:
        return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяем права пользователя как администратора."""
    if current_user.role.id in [3, 4]:
        return current_user
    raise ForbiddenException
