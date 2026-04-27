import os
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel

from api.auth import fake_user_db
# 规范导入：从依赖注入模块统一获取
from api.dependencies import get_current_user
from core.config import settings

router = APIRouter()


# --- 1. 数据模型 (Schemas) ---
class UserResponse(BaseModel):
    id: int
    username: str
    student_id: str
    avatar_url: Optional[str] = None
    # 可以在这里扩展更多字段，配合 Android 端的个人中心展示
    nickname: Optional[str] = "未设置昵称"
    bio: Optional[str] = "这个人很懒，什么都没留下"


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None


# --- 2. 个人资料接口 ---

@router.get("/me", response_model=UserResponse, summary="获取当前登录用户信息")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户的个人中心资料。Android 端打开“我的”页面时调用此接口。
    """
    # 确保返回的数据包含新扩展的字段
    return current_user


@router.put("/me", response_model=UserResponse, summary="修改个人资料")
async def update_user_me(user_in: UserUpdate, current_user: dict = Depends(get_current_user)):
    """
    更新当前登录用户的部分资料（如昵称、个性签名）。
    """
    username = current_user["username"]
    if username in fake_user_db:
        # 剔除未设置的字段，仅更新传过来的字段
        update_data = user_in.dict(exclude_unset=True)
        fake_user_db[username].update(update_data)
        return fake_user_db[username]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")


@router.post("/me/avatar", response_model=UserResponse, summary="上传/更新头像")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user)
):
    """
    接收 Android 端传来的图片文件，保存到本地服务器，并更新用户的 avatar_url。
    """
    # 1. 验证文件类型（防止恶意文件上传）
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片格式的文件")

    # 2. 确保头像存储的物理目录存在 (由 config.py 中的设置决定)
    os.makedirs(settings.AVATAR_DIR, exist_ok=True)

    # 3. 构造安全的文件名 (使用用户ID防止图片重名被覆盖)
    file_extension = file.filename.split(".")[-1]
    new_filename = f"user_{current_user['id']}_avatar.{file_extension}"
    file_path = os.path.join(settings.AVATAR_DIR, new_filename)

    # 4. 将文件流写入本地磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. 更新数据库中的头像网络访问路径
    # 这里存的是相对路径，Android 端需要拼接上服务器的 IP 和端口
    avatar_url = f"/static/avatars/{new_filename}"

    username = current_user["username"]
    fake_user_db[username]["avatar_url"] = avatar_url

    return fake_user_db[username]
