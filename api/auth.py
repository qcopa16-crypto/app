from typing import Any

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
# 导入安全工具、配置、依赖和业务层
from core import security
from crud import crud_user
from schemas.user_schema import UserCreate, UserLogin, TokenResponse

router = APIRouter()


# 注意：已经彻底删除了 fake_user_db 和本地的 Pydantic 模型定义，统一使用 schemas 目录下的模型

@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    接收用户注册信息，检查唯一性，加密密码并存入 MySQL 数据库。
    """
    # 1. 检查用户名是否已存在 (从数据库查询)
    db_user = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册",
        )

    # 2. 检查学号是否已存在
    db_student = crud_user.get_user_by_student_id(db, student_id=user_in.student_id)
    if db_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学号已被绑定",
        )

    # 3. 调用 CRUD 层创建用户 (加密逻辑已在 crud_user.create_user 中实现)
    new_user = crud_user.create_user(db, obj_in=user_in)

    # 4. 为新用户生成 JWT Token
    access_token = security.create_access_token(data={"sub": new_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "username": new_user.username
    }


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    """
    验证用户凭证，成功后下发 JWT Token。
    """
    # 1. 从数据库查询用户
    db_user = crud_user.get_user_by_username(db, username=user_in.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 2. 使用安全工具验证哈希密码
    if not security.verify_password(user_in.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 3. 签发 Token
    access_token = security.create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username
    }