import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 导入静态文件模块

from api import auth, tasks, users  # 导入 users 模块
from core.config import settings
from db.session import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# 跨域配置...
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 【新增】：挂载静态文件目录
# 确保物理文件夹存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
# 将物理目录 uploads 映射到网络路由 /static 上
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# 挂载业务路由
app.include_router(auth.router, prefix="/api/auth", tags=["鉴权模块"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务模块"])
# 【新增】：挂载用户中心路由
app.include_router(users.router, prefix="/api/users", tags=["用户模块"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
