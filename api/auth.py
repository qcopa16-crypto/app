from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core import security

# 假设你有一个依赖项用于获取数据库 Session： from app.api.dependencies import get_db

router = APIRouter()


# --- 1. 定义接口交互的数据模型 (Schemas) ---
# 实际项目中，这些类应该放在 app/schemas/user_schema.py 中
class UserCreate(BaseModel):
    username: str
    password: str
    student_id: str  # 学号，贴合校园场景


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


# --- 模拟数据库操作 (实际应用中请替换为 CRUD 层代码) ---
fake_user_db = {}
current_user_id = 1


# --- 2. 核心接口实现 ---

@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(user_in: UserCreate) -> Any:
    """
    接收用户注册信息，加密密码并存入数据库，注册成功后直接返回 Token 实现自动登录。
    """
    global current_user_id

    # 1. 检查用户是否已存在
    if user_in.username in fake_user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册",
        )

    # 2. 密码加密保存
    hashed_password = security.get_password_hash(user_in.password)

    # 3. 存入数据库 (模拟)
    new_user = {
        "id": current_user_id,
        "username": user_in.username,
        "student_id": user_in.student_id,
        "hashed_password": hashed_password
    }
    fake_user_db[user_in.username] = new_user
    current_user_id += 1

    # 4. 生成 Token
    access_token = security.create_access_token(data={"sub": new_user["username"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user["id"],
        "username": new_user["username"]
    }


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(user_in: UserLogin) -> Any:
    """
    验证用户凭证，成功后下发 JWT Token。
    """
    # 1. 查询用户
    user = fake_user_db.get(user_in.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 2. 验证密码
    if not security.verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 3. 签发 Token
    access_token = security.create_access_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"]
    }
