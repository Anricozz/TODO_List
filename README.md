# FocusList 待办清单

一个前后端分离的待办事项应用。前端使用原生 HTML、CSS 和 JavaScript，后端使用 FastAPI，待办数据存储在 MySQL。

## 当前功能

- 待办管理：新增、查看、编辑、删除任务
- 任务状态：支持完成/未完成切换、优先级、备注
- 任务筛选：支持全部、待完成、已完成和关键词搜索
- 接口文档：FastAPI 自动提供 Swagger UI

所有访问者读写同一份待办清单。

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

## 2. 后端
编辑 `backend/.env`，至少确认以下配置：

```dotenv
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
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

## REST API

所有接口以 `/api/v1` 开头，无需鉴权。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/todos` | 获取任务列表 |
| `POST` | `/todos` | 新建任务 |
| `GET` | `/todos/{id}` | 获取单个任务 |
| `PATCH` | `/todos/{id}` | 修改任务 |
| `DELETE` | `/todos/{id}` | 删除任务 |

`GET /todos` 还支持 `completed`、`search`、`skip` 和 `limit` 查询参数。

