# 这里假设你在 db/session.py 中定义了 Base = declarative_base()
from db.session import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, comment="任务标题")
    description = Column(String(500), nullable=True, comment="任务描述")
    deadline = Column(String(50), nullable=False, comment="截止日期 (YYYY-MM-DD)")
    priority = Column(Integer, default=1, comment="优先级: 1低 2中 3高")
    is_completed = Column(Boolean, default=False, comment="是否完成")
    created_at = Column(DateTime, comment="创建时间")

    # 外键关联到 users 表
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # ORM 关系映射，方便进行联合查询
    # user = relationship("User", back_populates="tasks")
