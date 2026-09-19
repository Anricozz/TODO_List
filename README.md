# FocusList 待办清单

前后端分离的待办事项应用。前端使用原生 HTML、CSS 和 JavaScript，后端使用 FastAPI，待办数据存储在 MySQL。

## 当前功能

- 用户体系：用户名 + 密码注册、登入，passlib 加密后入库，JWT 签发令牌
- 登录态：access token 3 分钟、refresh token 6 分钟，过期后需重新登入
- 待办管理：新增、查看、编辑、删除任务
- 任务状态：支持完成/未完成切换、优先级、备注
- 任务筛选：支持全部、待完成、已完成和关键词搜索
- 接口文档：FastAPI 自动提供 Swagger UI

每个用户只能读写属于自己的待办清单；登入前请先在前端登录页注册或登入。

## 项目结构

```
backend/
  app/
    config.py        # 全局配置（数据库、CORS、JWT 有效期等）
    database.py      # 引擎、Session 与 get_db 依赖
    core/            # 密码加密、JWT 签发/校验、当前用户依赖
    model/           # SQLAlchemy 建模：TODO 与 user
    schema/          # 请求体/响应体：通用封装、TODO、user
    crud/            # 数据库读写：TODO 与 user
    router/          # 路由：TODO 与 user（/auth）
    main.py          # 应用入口
  scripts/           # 建表脚本
frontend/
  index.html         # 待办主页面（需登入）
  login.html         # 注册 / 登入页面
  js/                # config、api、auth、app
```

## 安裝依賴

```
pip install -r requirements.txt
```

## 1. MySQL

1. 建立資料庫：

```sql
CREATE DATABASE TODO_List_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'list_manager'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON TODO_List_DB.* TO 'list_manager'@'localhost';
```

> 从 v0.2 开始 `todos` 表新增了 `user_id` 外键。升级时因为 `create_all` 不会修改已存在的表，
> 需要先删掉旧的 `todos` 表（旧数据会丢失），再启动后端，或手动执行 `backend/scripts/init_database.sql`。

## 2. 后端
编辑 `backend/.env`，至少确认以下配置：

```dotenv
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
JWT_SECRET=please-change-me-to-a-random-string-at-least-32-bytes
ACCESS_TOKEN_EXPIRE_SECONDS=180
REFRESH_TOKEN_EXPIRE_SECONDS=360
```
启动后端
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

启动后可访问：

- API 根地址：<http://127.0.0.1:8000/>
- Swagger 文档：<http://127.0.0.1:8000/docs>

## 3. 启动前端

另开一个 PowerShell 窗口：

```powershell
cd frontend
python -m http.server 5500
```

然后访问 <http://127.0.0.1:5500>。也可以使用Live Server 打开 `frontend/index.html`
如果后端或前端端口发生变化，请同步修改 `frontend/js/config.js` 和 `backend/.env` 中的 `CORS_ORIGINS`。

pycharm的浏览器开启不可，因为这个项目中浏览器'同源规则' 检测为开启状态。
## REST API

所有接口以 `/api/v1` 开头，成功响应统一为 `{"code": 0, "message": "...", "data": ...}`，错误仍为 `{"detail": "..."}`。

### 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/auth/register` | 注册（用户名 3-50 字符，密码 6-128 字符），返回双 token 并直接登入 |
| `POST` | `/auth/login` | 登入，返回双 token |
| `POST` | `/auth/refresh` | 用 refresh token 换新的 access token（refresh token 不轮换、不延期） |
| `GET` | `/auth/me` | 获取当前登入用户，需要 `Authorization: Bearer <access_token>` |

access token 默认 3 分钟失效，refresh token 默认 6 分钟失效；两者都失效后前端会清空本地凭据并回到登录页，不会自动登入。

### 待办

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/todos` | 获取任务列表 |
| `POST` | `/todos` | 新建任务 |
| `GET` | `/todos/{id}` | 获取单个任务 |
| `PATCH` | `/todos/{id}` | 修改任务 |
| `DELETE` | `/todos/{id}` | 删除任务 |

所有 `/todos` 接口都需要 `Authorization: Bearer <access_token>`，且只能操作自己的数据（访问他人的任务返回 404）。
`GET /todos` 还支持 `completed`、`search`、`skip` 和 `limit` 查询参数。
