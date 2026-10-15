# LangGraph Function-Calling Agent

用 LangGraph 框架重构的 Function-Calling Agent。
把手写的 Function-Calling 闭环，用"图"的方式表达：节点、边、条件路由。

## 项目背景

阶段3用手写 `while True` + `if-else` 实现了 Function-Calling 闭环。
本项目用 LangGraph 重构，体会框架如何把"流程"抽象成"图"。

## 核心原理

```
[START]
    ↓
[node_llm]         ← 调用大模型
    ↓
[条件路由 route]    ← 判断：要调工具吗？
    ├─ 要调 → [node_tool] → 回到 [node_llm]
    └─ 不调 → [END]
```

## 与手写版的对比

| 手写版 | LangGraph 版 |
|--------|-------------|
| `while True` | 图自动循环 |
| `if msg.get("tool_calls")` | `route` 条件路由 |
| `requests.post(...)` | `node_llm` 节点 |
| `func(**args)` | `node_tool` 节点 |
| `messages = []` | `AgentState` |

## 技术栈

- Python 3.8+
- LangGraph
- requests
- 智谱 GLM-4

## 功能

- 计算器
- 获取系统时间
- 添加备忘录

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
export ZHIPU_API_KEY="你的智谱Key"
```

### 3. 运行

```bash
python3 langgraph_agent.py
```

## 运行示例

```
👤 你: 3+5
🔧 调用工具：tool_calculator，结果：计算结果：8
🤖 Agent: 3+5等于8。

👤 你: 现在几点了
🔧 调用工具：tool_get_time，结果：🕐 当前时间：2026-10-15 22:30:00
🤖 Agent: 现在是2026年10月15日22点30分。
```

## 项目结构

```
langgraph-agent/
├── langgraph_agent.py    # 主程序
├── requirements.txt      # 依赖清单
├── README.md             # 项目说明
└── .gitignore            # Git忽略规则
```

## 学习收获

- 理解 LangGraph 的四大核心概念：State、节点、边、条件路由
- 掌握如何把 if-else 流程重构为图结构
- 理解框架如何规范化 Agent 开发

## License

MIT