from typing import Optional

from sqlalchemy.orm import Session

# 引入安全模块，用于注册时加密密码
from core.security import get_password_hash
# 假设你已经建立了对应的 SQLAlchemy 模型和 Pydantic 模型
from models.user import User
from schemas.user_schema import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    通过 ID 获取单个用户
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    通过用户名获取用户（登录时最核心的查询）
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_student_id(db: Session, student_id: str) -> Optional[User]:
    """
    通过学号获取用户（可用于注册时检查学号是否被占用）
    """
    return db.query(User).filter(User.student_id == student_id).first()


def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    创建新用户
    注意：API 层传来的是明文密码，CRUD 层负责将其转化为哈希密文后再存入数据库。
    """
    # 兼容 Pydantic V1 和 V2
    obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in.model_dump()

    # 将明文密码拿出来，加密后存为 hashed_password
    plain_password = obj_in_data.pop("password")
    hashed_password = get_password_hash(plain_password)

    # 创建 SQLAlchemy ORM 对象
    db_obj = User(
        **obj_in_data,
        hashed_password=hashed_password
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
    """
    更新用户资料（如修改昵称、个性签名、头像路径等）
    """
    # 获取原始数据库对象的字段
    obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}

    # 获取需要更新的传入字段，排除未设置的项
    update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in.model_dump(exclude_unset=True)

    # 如果更新包里包含了密码，需要重新哈希（比如未来增加的“修改密码”功能）
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    # 动态赋值更新
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
