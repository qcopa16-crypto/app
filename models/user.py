from datetime import datetime

# 这里假设你在 db/session.py 中定义了 Base = declarative_base()
from db.session import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="登录用户名")
    student_id = Column(String(20), unique=True, index=True, nullable=False, comment="学号")
    hashed_password = Column(String(255), nullable=False, comment="哈希加密后的密码")

    # 个人中心资料扩展字段
    nickname = Column(String(50), default="未设置昵称", comment="显示昵称")
    bio = Column(String(255), default="这个人很懒，什么都没留下", comment="个性签名")
    avatar_url = Column(String(255), nullable=True, comment="头像静态访问路径")

    is_active = Column(Boolean, default=True, comment="账号是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")

    # ORM 关联：一个用户对应多个任务
    # tasks = relationship("Task", backref="owner", cascade="all, delete-orphan")
