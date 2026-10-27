from flask import Blueprint, request, jsonify, Response, render_template
from pydantic import BaseModel, Field, ValidationError
import uuid
import time
import redis
import json  # 👈 核心修复：引入了 json

api_bp = Blueprint('api', __name__)

# 连接 Redis，用来存流式输出的进度
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

class TaskRequest(BaseModel):
    user_query: str = Field(..., max_length=200)

@api_bp.route('/')
def index():
    return render_template('index.html') # 渲染前端页面

@api_bp.route('/api/submit', methods=['POST'])
def submit_task():
    try:
        data = TaskRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": "参数错误", "detail": e.errors()}), 422
        
    task_id = str(uuid.uuid4())
    # 局部导入 Celery 任务，防止循环依赖
    from app.tasks import async_generate_report 
    
    # 丢给 Celery 后台去跑，立刻返回 task_id
    async_generate_report.delay(task_id, data.user_query, "daily_log.txt")
    return jsonify({"task_id": task_id})

# 【核心】SSE 流式推送接口
@api_bp.route('/api/stream/<task_id>')
def stream(task_id):
    def generate():
        last_text = ""
        while True:
            status = r.get(f"task:{task_id}:status")
            current_text = r.get(f"task:{task_id}:text") or ""
            
            # 只有产生新字了，才推给前端
            if current_text != last_text:
                # 计算新增的字
                new_chars = current_text[len(last_text):]
                
                # 👈 核心修复：用 json.dumps 包装，防止换行符破坏 SSE 格式
                yield f"data: {new_chars.replace(chr(10), ' ')}\n\n"
                last_text = current_text
                
            if status == "FINISHED":
                yield "data: [DONE]\n\n"
                break
                
            time.sleep(0.2) # 轮询频率
            
    # 👈 加上 headers 防止浏览器或代理缓存阻塞流
    return Response(generate(), mimetype='text/event-stream', headers={'X-Accel-Buffering': 'no', 'Cache-Control': 'no-cache'})
    # 在 app/api.py 最下面加上这个新路由
@api_bp.route('/api/history', methods=['GET'])
def get_history():
    # lrange 是从左边取，0 到 -1 代表取全部
    history_raw = r.lrange("history_list", 0, -1)
    # 把取出来的字符串转回 Python 列表字典
    history_data = [json.loads(item) for item in history_raw]
    return jsonify({"data": history_data})
