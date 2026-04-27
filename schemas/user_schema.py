from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- 1. 基础模型 (Base) ---
# 包含用户注册和返回时都会用到的公共字段
class UserBase(BaseModel):
    # Field 用于添加约束：用户名长度在 3-50 之间
    username: str = Field(..., title="用户名", min_length=3, max_length=50)
    student_id: str = Field(..., title="学号", min_length=4, max_length=20)


# --- 2. 注册/创建用户模型 (Create) ---
# 用于接收 Android 端 /api/auth/register 传来的 JSON 数据
# 必须包含明文密码
class UserCreate(UserBase):
    password: str = Field(..., title="密码", min_length=6, max_length=128, description="密码长度不能少于6位")

    # 为 Swagger UI 提供测试样例
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "zhangsan",
                "student_id": "2024001001",
                "password": "securepassword123"
            }
        }
    }


# --- 3. 更新用户资料模型 (Update) ---
# 用于接收 Android 端 /api/users/me (PUT) 传来的数据
# 这里不包含 username 和 student_id，意味着不允许用户自己修改登录名和学号
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, title="显示昵称", max_length=50)
    bio: Optional[str] = Field(None, title="个性签名", max_length=255)
    # 如果后续打算在个人中心增加“修改密码”功能，可以将此行取消注释
    # password: Optional[str] = Field(None, title="新密码", min_length=6)


# --- 4. 响应/返回结果模型 (Response) ---
# 用于向 Android 端返回用户信息 (自动剔除密码字段)
class UserResponse(UserBase):
    id: int
    nickname: str
    bio: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    # 关键配置：允许 Pydantic 读取 SQLAlchemy 的 ORM 对象并序列化为 JSON
    model_config = {
        "from_attributes": True
    }


# --- 5. 鉴权 Token 响应模型 (可选放入) ---
# 用于 /api/auth/login 返回的内容规范
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
