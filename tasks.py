import redis
from celery import Celery
from app.agent import run_agent_stream

# 用 Redis 作为中间人（Broker）
celery_app = Celery('agent_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# 连接 Redis，用来存流式输出的进度
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

@celery_app.task
def async_generate_report(task_id, user_query, filepath):
    # 告诉前端：任务开始了
    r.set(f"task:{task_id}:status", "PROCESSING")
    r.set(f"task:{task_id}:text", "")
    
    full_text = ""
    # 遍历流式生成器
    for chunk in run_agent_stream(user_query, filepath):
        full_text += chunk
        # 把每次生成的几个字，追加到 Redis 里
        r.set(f"task:{task_id}:text", full_text)
        
    # 告诉前端：任务完成了
    r.set(f"task:{task_id}:status", "FINISHED")
    return full_text