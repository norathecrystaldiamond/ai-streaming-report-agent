# 🚀 企业级 AI 流式报表助手 (AI Streaming Report Agent)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![Vue](https://img.shields.io/badge/Frontend-Vue3-42b883.svg)
![Celery](https://img.shields.io/badge/Async-Celery-37814A.svg)
![Redis](https://img.shields.io/badge/DB-Redis-DC382D.svg)
![LLM](https://img.shields.io/badge/LLM-DeepSeek-purple.svg)

## 📖 项目简介

本项目是一个**前后端分离的全栈 AI 提效应用**。针对传统 AI 应用“生成极慢、前端卡死”的痛点，采用 **Celery 异步任务队列** 与 **SSE 流式推送** 技术，实现了类似 ChatGPT 的打字机实时输出体验。

用户只需输入“流水账”，即可自动生成不同语气风格的结构化周报，并支持历史记录的持久化查询。

## ✨ 核心功能与工程亮点

1. **异步高可用架构 (Celery + Redis)**：AI 生成极其耗时，Flask 主线程接收请求后立刻返回 `TaskID`，将生成任务交由后台 Celery Worker 处理，彻底解决主线程阻塞问题，保障高并发性能。
2. **SSE 流式打字机体验 (Server-Sent Events)**：后端通过 `yield` 结合 Redis 缓存进度，前端通过 `EventSource` 接收字符流，实时渲染在页面上，大幅降低用户的等待焦虑。
3. **提示词意图前置拼装 (Prompt Engineering)**：前端通过 Vue 的双向绑定，将用户选择的“语气风格”（幽默、严肃、自定义）动态拼接至发给后端的指令中，无需增加复杂的后端传参即可实现千人千面的生成效果。
4. **持久化历史记录查询**：利用 Redis 的 `List` 数据结构，将每次成功生成的 `{时间, 需求, 结果}` 落盘，并提供 API 接口供前端实时拉取渲染。
5. **严格的数据校验 (Pydantic)**：使用 Pydantic 对前端传来的 JSON 进行类型与长度校验，防止恶意超长文本导致大模型 Token 被刷爆。

---

## 🏗️ 系统架构流转图

```text
[ Vue 3 前端 ]  ─── 1. 提交需求 (POST) ───►  [ Flask 后端接口 ]
      ▲                                           │
      │                                           │ 2. 抛入消息队列
      │ 5. 实时推送字符 (SSE)                        ▼
[ EventSource ] ◄── 4. 轮询读进度 ─── [ Redis 数据库 (Broker/缓存) ]
                                                  ▲
                                                  │ 3. 后台消费并调用大模型
                                            [ Celery Worker ]
                                                  │
                                                  ▼
                                            [ LangChain ] ──► [ DeepSeek API ]


🧗‍♂️ 踩坑记录与排错总结（核心价值）
在独立开发此项目时，解决了以下极具代表性的工程问题：

Redis 协议冲突：新版 redis-py 库默认使用 RESP3 协议（发送 HELLO 指令），导致 Windows 下的老旧 Redis Server 报错拒连。

解决：通过在代码中强制降级 redis==4.5.5 解决兼容性问题。

Vue 与 Jinja2 模板语法冲突：Flask 自带 Jinja2 引擎，与 Vue 的 {{ }} 插值语法打架，导致后端渲染 500 报错。

解决：在 HTML 文件中使用 {% raw %} ... {% endraw %} 将 Vue 代码块包裹，告诉 Flask 放弃解析该区域。

Windows 下 Celery 递归崩溃：使用 gevent 协程池与 LangChain 结合流式输出时，触发 maximum recursion depth exceeded 异常。

解决：改用 -P solo 单进程模式，并调高 Python 的 sys.setrecursionlimit 上限。

前端 SSE 断连与缓存阻塞：浏览器因代理缓存或换行符破坏 SSE 格式，导致前端无法看到打字效果。

解决：后端添加 headers={'X-Accel-Buffering': 'no', 'Cache-Control': 'no-cache'} 并处理了特殊字符。

🗺️ 后续迭代路线 (Roadmap)
□ 容器化隔离与部署：编写 Dockerfile 与 docker-compose.yml，将 Flask、Celery、Redis 编排启动，实现“一键跨平台运行”，消除环境差异。
□ 多模型抽象路由 (Provider Pattern)：实现统一的 LLM 接口抽象，支持在界面上无缝切换 DeepSeek、通义千问、Claude 等模型，拒绝单一厂商绑定。
□ 全链路可观测性：接入 LangSmith，实时追踪每次请求的耗时、Token 消耗与内部调用链路，为 Prompt 调优和成本控制提供数据支撑。

本地启动指南 (Windows)
本项目依赖 Redis 作为消息中间件与数据存储，需确保本地已运行 Redis 服务（如 redis-server.exe）。

1. 安装依赖包
打开终端，在项目根目录下执行：

bash
# 建议使用清华源加速下载
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
2. 启动服务（需打开 3 个终端窗口）
终端 1：启动 Celery 异步打工人
(注：Windows 环境下必须指定 -P solo 或 -P gevent，否则会引发进程池冲突)

bash
celery -A worker.celery_app worker --loglevel=info -P solo
终端 2：启动 Flask 主服务

bash
python run.py
终端 3：确保本地 Redis 已启动

bash
redis-server.exe
3. 访问应用
打开浏览器访问：👉 http://127.0.0.1:5000

