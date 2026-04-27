import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, get_db
# 导入配置、依赖、业务层和模型
from core.config import settings
from crud import crud_user
from models.user import User
from schemas.user_schema import UserResponse, UserUpdate

router = APIRouter()


# 注意：已经彻底删除了 fake_user_db，所有操作都通过 db: Session 进行

@router.get("/me", response_model=UserResponse, summary="获取当前登录用户信息")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户的个人中心资料。
    由于 get_current_user 已经从数据库查出了完整的 User 对象，这里直接返回即可。
    """
    return current_user


@router.put("/me", response_model=UserResponse, summary="修改个人资料")
async def update_user_me(
        user_in: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    更新当前登录用户的资料（如昵称、个性签名）。
    """
    return crud_user.update_user(db=db, db_obj=current_user, obj_in=user_in)


@router.post("/me/avatar", response_model=UserResponse, summary="上传/更新头像")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    接收图片文件，保存到服务器，并更新数据库中用户的头像路径。
    """
    # 1. 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能上传图片格式的文件")

    # 2. 确保存储目录存在
    os.makedirs(settings.AVATAR_DIR, exist_ok=True)

    # 3. 构造文件名 (使用用户 ID 确保唯一性)
    file_extension = file.filename.split(".")[-1]
    new_filename = f"user_{current_user.id}_avatar.{file_extension}"
    file_path = os.path.join(settings.AVATAR_DIR, new_filename)

    # 4. 保存文件到磁盘
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"文件保存失败: {str(e)}")

    # 5. 更新数据库中的头像网络访问路径
    # 存储相对路径，方便 Android 端拼接基础 URL
    avatar_url = f"/static/avatars/{new_filename}"

    # 构造一个只包含头像路径更新的对象
    update_data = UserUpdate()
    # 注意：如果 UserUpdate 中没有 avatar_url 字段，
    # 也可以直接手动调用 crud_user.update_user 的逻辑或在 crud 中扩展

    # 这里我们直接手动更新模型属性并提交，或者确保 UserUpdate 包含该字段
    setattr(current_user, "avatar_url", avatar_url)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
