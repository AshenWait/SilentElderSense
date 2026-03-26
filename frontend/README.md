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
│   │   ├── Login.vue        # 登录页
│   │   ├── Dashboard.vue    # 事件看板
│   │   ├── Analysis.vue     # 统计分析
│   │   ├── Monitor.vue      # 实时监控
│   │   ├── VideoDetect.vue  # 视频检测
│   │   ├── System.vue       # 系统管理
│   │   └── Visualization.vue # 可视化大屏
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
- 实时监控（摄像头实时检测）
- 视频检测（上传视频文件检测）
- 系统管理
- 可视化大屏

## WebSocket 接口

前端通过 WebSocket 与后端通信：

| 端点 | 用途 |
|------|------|
| `ws://localhost:8000/ws/video/<video_id>` | 视频文件处理（上传后处理） |
| `ws://localhost:8000/ws/detect/<video_id>` | 实时帧检测（摄像头） |

详细协议请参考 `backend/core/README.md`。