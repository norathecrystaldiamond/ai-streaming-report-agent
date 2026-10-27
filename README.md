# ai-streaming-report-agent
# 企业级 AI 流式周报助手

## 🚀 项目简介
基于 Flask + Vue 3 + Celery + Redis + SSE 构建的前后端分离 AI 应用。实现了长耗时 AI 任务的后台异步处理，以及类似 ChatGPT 的流式打字机输出。

## 🛠️ 启动指南（Windows 环境）
本项目需要同时启动 3 个终端窗口。

### 1. 启动 Redis (前提)
确保本地 Redis 服务正在运行（双击 `redis-server.exe` 或保证 Docker 容器运行）。

### 2. 启动 Celery 后台打工人
```bash
celery -A worker.celery_app worker --loglevel=info -P solo
