🎓 校园任务管理系统 (Campus Task Management API)
基于 Python 3 + FastAPI 构建的校园任务管理系统后端 RESTful API 服务。
本项目采用标准的前后端分离架构，提供高性能、异步的接口服务，支持完整的用户鉴权、任务流转及数据持久化，专为 Android / 移动端等前端应用设计。

✨ 核心特性 (Features)
⚡️ 高性能异步框架: 基于 FastAPI 构建，自动生成 OpenAPI (Swagger) 交互式文档。

🔒 安全鉴权体系: 使用 JWT (JSON Web Tokens) 进行无状态鉴权，密码采用 bcrypt 加盐哈希加密，确保校园数据安全。

📂 规范的工程目录: 严格遵循 API 路由 -> Schemas 校验 -> CRUD 操作 -> Models 映射 的分层架构，高内聚低耦合。

🗄️ ORM 数据管理: 深度集成 SQLAlchemy，告别原生 SQL 拼接，防止 SQL 注入。

👤 隔离的数据视图: 严格的越权校验机制，确保每位学生只能访问和修改自己的任务列表。

🖼️ 静态资源管理: 内置文件上传功能，支持用户头像与附件的本地持久化与静态路由映射。

🛠️ 技术栈 (Tech Stack)
核心框架: Python 3.8+ / FastAPI / Uvicorn

数据库交互: SQLAlchemy (ORM) / PyMySQL

数据验证: Pydantic V2

安全加解密: passlib[bcrypt] / python-jose[cryptography]

文件处理: python-multipart

📁 目录结构 (Project Structure)
Plaintext
├── api/                    # 📌 API 路由层 (Controllers)
│   ├── auth.py             # 注册、登录与 Token 分发接口
│   ├── dependencies.py     # 核心依赖注入 (解析Token、获取DB Session)
│   ├── tasks.py            # 任务增删改查业务接口
│   └── users.py            # 用户资料与头像上传接口
├── core/                   # ⚙️ 核心配置层
│   ├── config.py           # 环境变量与全局配置中心 (需自行配置)
│   └── security.py         # 密码哈希与 JWT 签发工具
├── crud/                   # 🛠️ 数据库操作层 (Create, Read, Update, Delete)
│   ├── crud_task.py        # 任务表相关 SQL 逻辑
│   └── crud_user.py        # 用户表相关 SQL 逻辑
├── db/                     # 🔌 数据库连接层
│   └── session.py          # SQLAlchemy 引擎与 Session 实例
├── models/                 # 🗄️ ORM 映射模型
│   ├── task.py             # Task 数据表结构
│   └── user.py             # User 数据表结构
├── schemas/                # 🛡️ 数据校验与序列化模型 (Pydantic)
│   ├── task_schema.py      # Task 请求/响应体定义
│   └── user_schema.py      # User 请求/响应体定义
├── main.py                 # 🚀 FastAPI 启动主入口
└── test_main.http          # 📝 HTTP 接口简易测试脚本
(注：为保障安全，数据库连接信息、core/ 及 db/ 下的部分敏感配置文件未提交至代码库。)

🚀 快速启动 (Getting Started)
1. 环境准备
确保你的电脑上已安装 Python 3.8 或以上版本，以及 MySQL 数据库。

Bash
# 1. 克隆项目到本地
git clone https://github.com/qcopa16-crypto/app.git
cd app

# 2. 创建并激活虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Windows 下使用: venv\Scripts\activate

# 3. 安装依赖包
pip install fastapi uvicorn sqlalchemy pymysql pydantic-settings passlib[bcrypt] python-jose[cryptography] python-multipart
2. 数据库配置
在 MySQL 中创建一个数据库（例如 campus_task_db）。
请确保你已经补全了 core/config.py 和 db/session.py 文件，并在 .env 文件中配置好你的数据库连接字符串和 JWT 密钥：

代码段
# 示例 .env 环境变量
SECRET_KEY="your-super-secret-key"
MYSQL_SERVER="127.0.0.1"
MYSQL_USER="root"
MYSQL_PASSWORD="yourpassword"
MYSQL_DB="campus_task_db"
3. 运行服务
在项目根目录（main.py 所在目录）下执行启动命令：

Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
服务成功启动后，控制台会显示 Application startup complete.

📖 接口文档 (API Documentation)
得益于 FastAPI 的特性，项目启动后会自动生成实时可交互的接口文档。

Swagger UI (推荐): 访问 http://127.0.0.1:8000/docs

你可以在这里直接点击 "Try it out" 测试注册、登录（获取 Token）、添加任务等全套流程。

ReDoc: 访问 http://127.0.0.1:8000/redoc

📱 客户端对接说明 (For Android/Frontend)
统一鉴权头: 登录成功获取 access_token 后，后续请求其他接口均需在 HTTP 请求 Header 中携带该 Token：

HTTP
Authorization: Bearer <your_access_token>
静态资源访问: 通过 /me/avatar 接口上传头像后，返回的路径为 /static/avatars/xxx.jpg。客户端展示时需拼接完整的服务器地址，如 http://10.0.2.2:8000/static/avatars/xxx.jpg。

本地联调 IP: 若使用 Android 官方模拟器，请求本机的接口请使用 http://10.0.2.2:8000 而非 127.0.0.1。
