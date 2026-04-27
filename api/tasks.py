from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

# 规范导入：统一从依赖文件获取当前用户
from api.dependencies import get_current_user

router = APIRouter()


# --- 1. 数据模型 (Schemas) ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: str
    priority: int = 1  # 1:低, 2:中, 3:高


class TaskCreate(TaskBase):
    class Config:
        # 为 Swagger UI 提供默认的测试样例
        schema_extra = {
            "example": {
                "title": "优化CTG信号分割模型",
                "description": "调整UNet架构，处理早停机制导致轮数不同的控制变量问题",
                "deadline": "2026-05-10",
                "priority": 3
            }
        }


class TaskUpdate(TaskBase):
    is_completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: str


# 模拟任务数据库 (后期可替换为 MySQL)
fake_task_db = []
current_task_id = 1


# --- 2. 任务接口 (CRUD) ---

@router.post("/", response_model=TaskResponse, summary="创建新任务")
async def create_task(task_in: TaskCreate, current_user: dict = Depends(get_current_user)):
    """
    创建一个新任务，自动将其与当前登录的用户绑定。
    """
    global current_task_id
    new_task = {
        "id": current_task_id,
        "user_id": current_user["id"],  # 强制绑定当前用户的 ID
        "title": task_in.title,
        "description": task_in.description,
        "deadline": task_in.deadline,
        "priority": task_in.priority,
        "is_completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    fake_task_db.append(new_task)
    current_task_id += 1
    return new_task


@router.get("/", response_model=List[TaskResponse], summary="获取我的任务列表")
async def read_tasks(current_user: dict = Depends(get_current_user)):
    """
    获取任务列表。通过数据隔离，只返回属于当前用户的任务。
    """
    user_tasks = [task for task in fake_task_db if task["user_id"] == current_user["id"]]
    # 按照优先级降序，截止日期升序排列
    user_tasks.sort(key=lambda x: (-x["priority"], x["deadline"]))
    return user_tasks


@router.put("/{task_id}", response_model=TaskResponse, summary="更新任务信息")
async def update_task(task_id: int, task_in: TaskUpdate, current_user: dict = Depends(get_current_user)):
    """
    修改指定任务（仅限自己的任务）。
    """
    for index, task in enumerate(fake_task_db):
        if task["id"] == task_id:
            # 越权拦截：如果该任务不是当前用户的，拒绝操作
            if task["user_id"] != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改他人的任务")

            # 更新字段 (注意：Pydantic v2 中 dict() 建议改为 model_dump()，此处兼容你的写法)
            fake_task_db[index].update(task_in.dict(exclude_unset=True))
            return fake_task_db[index]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")


@router.delete("/{task_id}", summary="删除任务")
async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    """
    删除指定任务。
    """
    for index, task in enumerate(fake_task_db):
        if task["id"] == task_id:
            if task["user_id"] != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除他人的任务")

            fake_task_db.pop(index)
            return {"message": "任务删除成功"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")


@router.put("/{task_id}/complete", response_model=TaskResponse, summary="快捷切换任务完成状态")
async def toggle_task_complete(task_id: int, current_user: dict = Depends(get_current_user)):
    """
    快捷接口：用于 Android 端点击复选框时，直接反转任务的完成状态。
    """
    for index, task in enumerate(fake_task_db):
        if task["id"] == task_id:
            if task["user_id"] != current_user["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作他人的任务")

            fake_task_db[index]["is_completed"] = not fake_task_db[index]["is_completed"]
            return fake_task_db[index]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
