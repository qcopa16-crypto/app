from datetime import datetime

from sqlalchemy.orm import Session

# 这里假设你已经建立好了 SQLAlchemy 的模型 (models) 和 Pydantic 的校验模型 (schemas)
from models.task import Task
from schemas.task_schema import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int):
    """
    通过 ID 获取单个任务
    """
    return db.query(Task).filter(Task.id == task_id).first()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    获取指定用户的所有任务，并支持分页。
    默认按照优先级降序（3->1），截止日期升序（最近的在前面）排列。
    """
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .order_by(Task.priority.desc(), Task.deadline.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_task(db: Session, obj_in: TaskCreate, user_id: int):
    """
    创建新任务并绑定到指定用户
    """
    # 将 Pydantic 模型转换为字典 (Pydantic V2 推荐用 model_dump()，V1 用 dict())
    obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in.model_dump()

    # 创建 SQLAlchemy 模型实例
    db_obj = Task(
        **obj_in_data,
        user_id=user_id,
        is_completed=False,
        created_at=datetime.now()
    )

    # 写入数据库
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)  # 刷新实例以获取数据库自动生成的 ID
    return db_obj


def update_task(db: Session, db_obj: Task, obj_in: TaskUpdate):
    """
    更新现有任务
    注意：这里的入参 db_obj 是已经从数据库中查询出来的 SQLAlchemy 对象
    """
    # 获取原始数据
    obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}

    # 获取需要更新的数据 (排除未传入的字段)
    update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in.model_dump(exclude_unset=True)

    # 动态赋值
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_task(db: Session, task_id: int):
    """
    删除任务
    """
    db_obj = db.query(Task).filter(Task.id == task_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
