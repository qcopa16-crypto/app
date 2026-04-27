from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

# 导入依赖项
from api.dependencies import get_current_user, get_db
from crud import crud_task
from models.user import User  # 用于类型提示
from schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


# 注意：已经删除了 fake_task_db 和本地的 get_current_user 定义

@router.post("/", response_model=TaskResponse, summary="创建新任务")
async def create_task(
        task_in: TaskCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    创建一个新任务，并将其与当前登录用户的 ID 绑定。
    """
    return crud_task.create_task(db=db, obj_in=task_in, user_id=current_user.id)


@router.get("/", response_model=List[TaskResponse], summary="获取我的任务列表")
async def read_tasks(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    """
    获取当前用户的所有任务。CRUD 层已处理好优先级排序。
    """
    return crud_task.get_user_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.put("/{task_id}", response_model=TaskResponse, summary="更新任务信息")
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    修改指定任务。包含越权检查，确保只能修改自己的任务。
    """
    db_obj = crud_task.get_task(db=db, task_id=task_id)
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改他人的任务")

    return crud_task.update_task(db=db, db_obj=db_obj, obj_in=task_in)


@router.delete("/{task_id}", summary="删除任务")
async def delete_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    删除任务。包含越权检查。
    """
    db_obj = crud_task.get_task(db=db, task_id=task_id)
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除他人的任务")

    crud_task.delete_task(db=db, task_id=task_id)
    return {"message": "任务删除成功"}


@router.put("/{task_id}/complete", response_model=TaskResponse, summary="切换任务完成状态")
async def toggle_task_complete(
        task_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    快捷切换任务的完成状态，常用于 Android 端的 CheckBox 点击操作。
    """
    db_obj = crud_task.get_task(db=db, task_id=task_id)
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    if db_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作他人的任务")

    # 复用 update 逻辑，只修改 is_completed 字段
    update_data = TaskUpdate(is_completed=not db_obj.is_completed)
    return crud_task.update_task(db=db, db_obj=db_obj, obj_in=update_data)
