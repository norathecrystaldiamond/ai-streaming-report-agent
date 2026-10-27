import redis
import json  # 👈 新增：必须要导入 json 库
from celery import Celery
from app.agent import run_agent_stream

celery_app = Celery('agent_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

@celery_app.task
def async_generate_report(task_id, user_query, filepath):
    r.set(f"task:{task_id}:status", "PROCESSING")
    r.set(f"task:{task_id}:text", "")
    
    full_text = ""
    for chunk in run_agent_stream(user_query, filepath):
        full_text += chunk
        r.set(f"task:{task_id}:text", full_text)
        
    # 👈 关键修复：把 rpush 放到 for 循环的外面（等整篇文章全写完再存）
    r.set(f"task:{task_id}:status", "FINISHED")
    
    # 组装要保存的数据
    history_data = {
        "task_id": task_id,
        "time": "2026-10-27", # 简单点，先写死，或者用 datetime 模块取当前时间
        "user_query": user_query,
        "result": full_text
    }
    # 转换成 JSON 字符串，ensure_ascii=False 是为了让中文正常显示
    r.rpush("history_list", json.dumps(history_data, ensure_ascii=False))
    
    return full_text
