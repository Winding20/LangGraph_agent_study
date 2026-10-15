import os
import json
import datetime
import sqlite3
import requests
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# ============ ① 配置 ============
API_KEY = os.environ.get("ZHIPU_API_KEY")
if not API_KEY:
    raise ValueError("❌ 请设置环境变量 ZHIPU_API_KEY")

URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
# ============ ② 工具函数 ============
def tool_calculator(expr):
    try:
        return f"计算结果：{eval(expr)}"
    except Exception as e:
        return f"计算错误：{e}"

def tool_get_time():
    return f"🕐 当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def tool_memo_add(content):
    conn = sqlite3.connect('memo.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS memo (id INTEGER PRIMARY KEY, content TEXT, created_at TEXT)")
    cursor.execute("INSERT INTO memo (content, created_at) VALUES (?, ?)",
                   (content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return f"✅ 已添加备忘录：{content}"

TOOL_MAP = {
    "tool_calculator": tool_calculator,
    "tool_get_time": tool_get_time,
    "tool_memo_add": tool_memo_add,
}

# ============ ③ 工具描述 ============
tools = [
    {"type": "function", "function": {"name": "tool_calculator", "description": "计算数学表达式",
        "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}, "required": ["expr"]}}},
    {"type": "function", "function": {"name": "tool_get_time", "description": "获取当前系统时间",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "tool_memo_add", "description": "添加一条备忘录",
        "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}}},
]

# ============ ④ State ============
class AgentState(TypedDict):
    messages: List[dict]

# ============ ⑤ 节点1：调用大模型 ============
def node_llm(state):
    resp = requests.post(
        url=URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "glm-4-flash", "messages": state["messages"], "tools": tools}
    )
    msg = resp.json()["choices"][0]["message"]
    return {"messages": state["messages"] + [msg]}

# ============ ⑥ 节点2：执行工具 ============
def node_tool(state):
    msg = state["messages"][-1]
    tool_call = msg["tool_calls"][0]
    func_name = tool_call["function"]["name"]
    args = json.loads(tool_call["function"]["arguments"])
    
    result = TOOL_MAP[func_name](**args)
    print(f"🔧 调用工具：{func_name}，结果：{result}")
    
    tool_msg = {
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "content": result
    }
    return {"messages": state["messages"] + [tool_msg]}

# ============ ⑦ 条件路由 ============
def route(state):
    last_msg = state["messages"][-1]
    if last_msg.get("tool_calls"):
        return "node_tool"
    else:
        return END

# ============ ⑧ 构建图 ============
graph = StateGraph(AgentState)
graph.add_node("node_llm", node_llm)
graph.add_node("node_tool", node_tool)
graph.set_entry_point("node_llm")
graph.add_conditional_edges("node_llm", route)
graph.add_edge("node_tool", "node_llm")
app = graph.compile()

# ============ ⑨ 主程序 ============
if __name__ == "__main__":
    while True:
        user_input = input("\n👤 你: ").strip()
        if user_input in ["exit", "quit", "退出"]:
            break
        if not user_input:
            continue
        
        state = {"messages": [{"role": "user", "content": user_input}]}
        result = app.invoke(state)
        
        final = result["messages"][-1]["content"]
        print(f"🤖 Agent: {final}")