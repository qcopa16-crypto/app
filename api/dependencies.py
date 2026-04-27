from typing import Generator

from db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from core.config import settings
from crud import crud_user

# 声明 OAuth2 规范，tokenUrl 指向登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# --- 1. 真实的数据库连接依赖 ---
def get_db() -> Generator:
    """
    获取数据库会话。
    每次请求创建一个 Session，请求结束自动关闭，确保资源不泄露。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 2. 真实的鉴权与当前用户获取 ---
async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> dict:
    """
    解析 JWT Token，并从 MySQL 数据库中获取当前登录的用户对象。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="凭证无效或已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. 解码 Token 载荷
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. 调用 crud_user 从数据库真实查询用户
    user = crud_user.get_user_by_username(db, username=username)

    # 3. 验证用户是否存在
    if user is None:
        raise credentials_exception

    return user