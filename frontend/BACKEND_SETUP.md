# 后端登录接口设置说明

## 初始化步骤

### 1. 创建数据库和测试用户

在 `SilentElderSense/backend` 目录下运行：

```bash
cd SilentElderSense/backend
python tools/init_users.py
```

这将创建以下测试用户：
- 管理员：admin / admin123
- 家属：family / family123
- 监护人：monitor / monitor123

### 2. 启动后端服务

```bash
python app.py
```

后端将在 `http://localhost:8000` 启动

## API 接口

### 登录接口

- **URL**: `POST http://localhost:8000/api/login`
- **请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

- **成功响应** (200):
```json
{
  "message": "登录成功",
  "token": "token-1-1711234567",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "admin",
    "role": "admin"
  }
}
```

- **失败响应** (401):
```json
{
  "error": "用户名或密码错误"
}
```

### 用户角色

- `admin`: 系统管理员，可以访问系统管理页面
- `family`: 家属用户
- `monitor`: 监护人

## 前端配置

前端已配置为连接到 `http://localhost:8000/api`，配置文件位于 `frontend/src/api/index.js`。

如需修改后端地址，请编辑该文件中的 `baseURL`。

## 注意事项

1. 确保 CORS 配置正确（已在 `app.py` 中配置）
2. 确保 SQLite 数据库文件已创建
3. 前端和后端需要同时运行
4. 登录后 token 会保存在 localStorage 中