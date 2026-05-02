# 🎓 校园任务管理系统 (Campus Task Management System)

本项目是一套完整的**前后端分离**校园任务管理解决方案。后端基于 **Python FastAPI** 构建高性能异步 API，移动端采用 **Android 原生 (Java)** 开发。系统旨在帮助学生高效管理日常学习任务，支持实时同步与个性化资料维护。

---

## ✨ 核心特性

### 1. 鉴权与安全
* **JWT 无状态鉴权**：基于 JSON Web Token 的认证机制，确保接口访问安全。
* **密码加盐加密**：后端采用 `bcrypt` 算法对用户密码进行哈希存储。
* **自动登录逻辑**：客户端实现 Token 持久化，启动时自动校验登录状态。

### 2. 任务管理 (CRUD)
* **全生命周期控制**：支持任务的新建、查询、编辑修改以及滑动删除。
* **状态实时切换**：支持点击 CheckBox 快速标记任务完成情况，并同步至服务器。
* **交互优化**：集成 `SwipeRefreshLayout` 实现下拉刷新，以及 `ItemTouchHelper` 实现侧滑删除。

### 3. 个人中心与资源
* **资料修改**：支持用户自定义修改昵称与个人签名。
* **头像上传系统**：支持调用系统相册选取图片，通过 `Multipart` 接口上传，并使用 `Glide` 实现网络头像异步加载。
* **静态资源服务**：后端自动映射物理路径，支持通过 URL 访问用户头像等资源。

---

## 🛠️ 技术栈

| 模块 | 技术选型 |
| :--- | :--- |
| **后端框架** | Python 3.8+ / FastAPI / Uvicorn |
| **数据库** | MySQL / SQLAlchemy (ORM) / PyMySQL |
| **数据模型** | Pydantic V2 |
| **Android 网络** | Retrofit 2 / OkHttp 3 / Gson |
| **图片处理** | Glide 4 (加载) / MultipartBody (上传) |
| **UI 交互** | Material Design / RecyclerView / SwipeRefreshLayout |

---

## 📂 项目目录说明

### 后端目录 (`backend/`)
```plaintext
├── api/                # API 路由 (Auth, Tasks, Users)
├── core/               # 核心配置 (JWT 签发、安全工具)
├── crud/               # 数据库 CRUD 封装逻辑
├── db/                 # 数据库连接与会话管理
├── models/             # SQLAlchemy 数据模型 (表结构)
├── schemas/            # Pydantic 校验模型 (输入输出格式)
└── main.py             # 项目启动入口与静态文件挂载
Android 目录 (android/)
Plaintext
├── api/                # 网络层：Retrofit 接口定义与拦截器
├── model/              # 数据实体类 (POJO)
├── ui/                 # Activity 与 Adapter 业务逻辑
└── utils/              # 工具类：SharedPreferences 管理
🚀 快速启动
1. 后端部署
安装环境：确保 Python 3.8+ 环境并安装依赖：

Bash
pip install fastapi uvicorn sqlalchemy pymysql pydantic-settings passlib[bcrypt] python-jose[cryptography] python-multipart
配置数据库：在 core/config.py 中设置 MySQL 连接字符串。

运行服务：

Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
2. Android 客户端调试
修改 IP 地址：在 RetrofitClient.java 中将 BASE_URL 修改为服务器地址。

注：Android 模拟器访问本机请使用 http://10.0.2.2:8000/。

权限配置：确保 AndroidManifest.xml 中已开启 INTERNET 权限。

运行项目：使用 Android Studio 同步 Gradle 并运行。

📖 接口文档
项目启动后访问：

Swagger UI (交互式): http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc
