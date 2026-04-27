from typing import Generator

from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# 如果你后续接入了真实的 MySQL，这里应该导入 SessionLocal
# from app.db.session import SessionLocal
# from app.crud import crud_user

# 声明 OAuth2 的规范，告诉 Swagger UI 和客户端去哪个接口换取 Token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login" if hasattr(settings, 'API_V1_STR') else "/api/auth/login")


# --- 1. 数据库连接依赖 ---
def get_db() -> Generator:
    """
    获取数据库会话的依赖函数。
    每次接口请求到来时创建一个数据库连接，接口处理完毕后自动关闭连接。
    (目前先写好标准框架，等你接入 MySQL 时解开注释即可)
    """
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()

    # 在未接入 MySQL 前，我们 yield 一个 None 占位
    yield None


# --- 2. 鉴权与当前用户依赖 ---
# 为了演示，我们暂时导入 auth.py 中的模拟数据库
from api.auth import fake_user_db


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db=Depends(get_db)  # 预留了 db 参数，为后续连接 MySQL 做准备
) -> dict:
    """
    解析请求头中的 JWT Token，验证身份并返回当前用户信息。
    任何需要登录才能访问的接口，只需要在参数里加上 Depends(get_current_user) 即可。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="凭证无效或已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. 解码 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. 从数据库中查询该用户
    # 如果接入了 MySQL，代码应该是： user = crud_user.get_by_username(db, username=username)
    user = fake_user_db.get(username)

    # 3. 验证用户是否存在
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: dict = Depends(get_current_user),
) -> dict:
    """
    进阶鉴权：在获取当前用户的基础上，进一步判断用户是否被封号/禁用。
    （可以在后续扩展使用，让系统更完善）
    """
    # 假设数据库中有 is_active 字段
    if current_user.get("is_active") is False:
        raise HTTPException(status_code=400, detail="该账号已被停用")
    return current_user
