# 前端项目说明

## 项目结构

```
frontend/
├── src/
│   ├── api/          # API 接口封装
│   ├── components/   # Vue 组件
│   ├── layouts/      # 布局组件
│   ├── router/       # 路由配置
│   ├── stores/       # Pinia 状态管理
│   ├── styles/       # 样式文件
│   ├── utils/        # 工具函数
│   ├── views/        # 页面组件
│   ├── App.vue       # 根组件
│   └── main.js       # 入口文件
├── index.html        # HTML 模板
├── package.json      # 依赖配置
└── vite.config.js    # Vite 配置
```

## 安装依赖

```bash
cd frontend
npm install
```

## 启动开发服务器

```bash
npm run dev
```

服务将在 `http://localhost:3000` 启动

## 构建生产版本

```bash
npm run build
```

## 预览生产构建

```bash
npm run preview
```

## 后端 API 配置

前端默认连接到 `http://localhost:8000` 的后端 API。

如需修改后端地址，请编辑 `src/api/index.js` 文件。

## 功能特性

- 用户登录认证
- 事件看板
- 统计分析
- 实时监控
- 系统管理
- 可视化大屏
- **流式视频上传与实时检测**（新增）

## WebSocket 连接

视频流上传功能使用 WebSocket 连接到后端：
- WebSocket 地址：`ws://localhost:8000/ws/video`
- 协议详情请参考项目根目录的 `VIDEO_STREAM_GUIDE.md`