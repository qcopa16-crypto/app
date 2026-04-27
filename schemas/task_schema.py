from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- 1. 基础模型 (Base) ---
# 包含所有 Task 相关的共有字段
class TaskBase(BaseModel):
    title: str = Field(..., title="任务标题", max_length=100)
    description: Optional[str] = Field(None, title="任务描述", max_length=500)
    deadline: str = Field(..., title="截止日期", description="格式推荐为 YYYY-MM-DD")
    priority: int = Field(1, title="优先级", description="1:低, 2:中, 3:高", ge=1, le=3)


# --- 2. 创建任务模型 (Create) ---
# 用于接收 Android 端新建任务时传来的数据
class TaskCreate(TaskBase):
    # Pydantic V2 推荐的 Swagger UI 示例配置方式
    # 提供贴合实际工作流的测试样例，方便直接在 Swagger 中点击 Try it out
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "优化一维信号分割模型",
                "description": "跑通UNet基线，重点分析由于早停机制导致训练轮数不同时，控制变量是否严格的问题",
                "deadline": "2026-05-15",
                "priority": 3
            }
        }
    }


# --- 3. 更新任务模型 (Update) ---
# 用于接收 Android 端修改任务时传来的数据
# 因为是更新，所以所有字段都设为 Optional（可选），前端传了哪个字段就更新哪个
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    deadline: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    is_completed: Optional[bool] = None


# --- 4. 响应/返回结果模型 (Response) ---
# 用于查询任务时，从数据库读取并序列化后返回给 Android 端的数据
class TaskResponse(TaskBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime

    # 关键配置：允许 Pydantic 直接读取 SQLAlchemy 的 ORM 模型对象
    # (Pydantic V1 中叫 orm_mode = True)
    model_config = {
        "from_attributes": True
    }
