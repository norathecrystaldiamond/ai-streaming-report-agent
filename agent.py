import sys
sys.setrecursionlimit(10000) # 把默认的1000层限制改成10000层
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def run_agent_stream(user_query, filepath):
    # 1. 真实读取文件
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
            yield f"📂 成功读取文件 {filepath}，共 {len(file_content)} 字。\n\n"
        else:
            file_content = "无文件内容"
            yield f"⚠️ 未找到文件 {filepath}，将仅根据需求生成。\n\n"
    except Exception as e:
        file_content = "读取失败"
        yield f"❌ 读取文件报错: {e}\n\n"

    # 2. 初始化真实大模型
    llm = ChatOpenAI(
        model="deepseek-chat", 
        api_key="sk-7fd8cafa932d4a67ad05ebd785342563",
        base_url="https://api.deepseek.com",
        temperature=0.8,
        streaming=True # 开启流式
    )

    # 3. 构建提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个资深互联网冲浪选手。请根据用户提供的流水账，写一份周报。格式要求包含：【本周工作总结】、【遇到的问题及解决】、【下周计划】。必须大量使用流行语（如：打工人、内卷、摸鱼、emo了、拿捏）。"),
        ("user", "这是我的流水账：\n{content}\n\n我的额外要求：{query}")
    ])

    # 4. 组装链并流式输出
    chain = prompt | llm
    
    try:
        # 遍历大模型返回的每一个字
        for chunk in chain.stream({"content": file_content, "query": user_query}):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        yield f"\n❌ 大模型生成失败: {e}"