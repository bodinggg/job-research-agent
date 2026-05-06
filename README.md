# Job Research Agent

多Agent AI系统，用于自动化求职研究。基于LangGraph、LangChain构建，使用SiliconFlow API（OpenAI兼容）。

## 功能特性

- **多Agent协作**：四个专业Agent（规划师、研究员、作者、评论家）协调工作
- **并行搜索**：多研究维度并发网络搜索
- **质量控制**：自动报告评估与自我修正循环
- **持续对话**：支持对报告进行追问，获取更深入的信息
- **会话管理**：保存研究历史，随时切换对比

## 架构图

### 研究流程（多Agent协作）

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Planner   │────▶│  Researcher │────▶│    Writer   │────▶│    Critic   │
│   Agent     │     │   Agent     │     │   Agent     │     │   Agent     │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                       │
                                                    ┌──────────────────┘
                                                    │ (score < 7)
                                                    ▼
                                              ┌─────────────┐
                                              │   Rewrite   │
                                              │    Loop     │
                                              └─────────────┘
```

### 对话流程（持续交互）

```
用户输入 ──▶ IntentDetector ──▶ Router ──┬──▶ 研究流程（new_research）
                                          │
                                          └──▶ 对话流程
                                                  │
                                    ┌─────────────┴─────────────┐
                                    ▼                           ▼
                            ┌───────────────┐           ┌───────────────┐
                            │ ContextAssembler│           │ResponseGenerator│
                            │ (RAG检索+历史) │           │ (LLM生成回答) │
                            └───────────────┘           └───────┬───────┘
                                    │                           │
                                    └─────────────┬───────────────┘
                                                  ▼
                                          ┌───────────────┐
                                          │MessageRepository│
                                          │  (保存历史)    │
                                          └───────────────┘
```

### 完整系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Streamlit UI                                 │
│   研究表单  │  报告展示  │  对话区域  │  会话历史侧边栏               │
└──────────────────────────────┬────────────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼────────────────────────────────────────┐
│                           FastAPI Backend                              │
│   POST /research  │  POST /dialogue  │  GET /sessions/{id}/history   │
└──────────────────────────────┬────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌───────────┐   ┌───────────┐   ┌───────────┐
       │  Storage  │   │Conversation│   │  Graph    │
       │Repository │   │  Module   │   │ Workflow  │
       └───────────┘   └───────────┘   └───────────┘
```

## 技术栈

- **LangGraph**：多Agent工作流编排，状态机实现
- **LangChain**：LLM提示词管理与链式调用
- **FastAPI**：高性能异步API后端
- **Streamlit**：交互式Web UI
- **SiliconFlow API**：OpenAI兼容接口（使用Qwen模型）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/job-research-agent.git
cd job-research-agent
```

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 配置环境

```bash
cp .env.example .env
# 编辑 .env 添加你的 SILICONFLOW_API_KEY
```

从 [siliconflow.cn](https://siliconflow.cn) 获取API密钥

### 4. 启动后端

```bash
uvicorn src.api.main:app --reload --port 8002
```

### 5. 启动前端（新终端）

```bash
streamlit run src/ui/app.py
```

打开 http://localhost:8501

## 项目结构

```
job-research-agent/
├── pyproject.toml              # 项目依赖
├── docker-compose.yml           # Qdrant部署（可选）
├── src/
│   ├── config.py               # 配置管理
│   ├── llm.py                  # LLM客户端工厂
│   ├── think_log.py            # 思考过程日志
│   ├── api/main.py             # FastAPI后端
│   ├── agents/                  # Agent实现
│   │   ├── planner.py           # 规划Agent
│   │   ├── researcher.py        # 研究Agent
│   │   ├── writer.py            # 写作Agent
│   │   └── critic.py            # 评审Agent
│   ├── graph/
│   │   ├── state.py             # 状态定义
│   │   └── workflow.py          # LangGraph工作流
│   ├── storage/                  # 持久化层
│   │   ├── models.py            # 数据模型
│   │   ├── repository.py        # 仓储模式
│   │   └── qdrant_client.py     # 向量存储
│   ├── conversation/            # 对话模块
│   │   ├── detector.py          # 意图检测
│   │   ├── router.py            # 请求路由
│   │   ├── context.py           # RAG上下文组装
│   │   └── generator.py         # 对话生成
│   └── ui/app.py                # Streamlit前端
└── tests/
    ├── test_agents.py           # Agent测试
    ├── test_storage.py          # 存储测试
    └── test_conversation.py     # 对话测试
```

## API接口

### POST /research

研究公司职位，返回研究报告。

```bash
curl -X POST http://localhost:8002/research \
  -H "Content-Type: application/json" \
  -d '{"company": "字节跳动", "position": "后端工程师"}'
```

响应：
```json
{
  "session_id": "uuid",
  "report": "# 字节跳动后端工程师研究报告\n\n...",
  "quality_score": 8.5,
  "research_plan_count": 6,
  "rewrite_count": 0,
  "messages": ["规划师: 创建了包含6个维度的研究计划", ...]
}
```

### POST /dialogue

针对已有报告进行对话追问。

```bash
curl -X POST http://localhost:8002/dialogue \
  -H "Content-Type: application/json" \
  -d '{"query": "技术栈主要是Java还是Go？", "session_id": "uuid"}'
```

响应：
```json
{
  "message_id": "uuid",
  "answer": "根据研究报告，字节跳动后端主要使用Go语言...",
  "source": "report"
}
```

### GET /sessions

列出所有研究会话。

### GET /sessions/{id}/history

获取会话对话历史。

## 开发

### 运行测试

```bash
pytest tests/ -v
```

### 代码覆盖率

```bash
pytest tests/ --cov=src --cov-report=html
```

## 展示技能点

1. **LangGraph状态机**：使用`StateGraph`与条件边进行工作流编排
2. **多Agent协作**：监督者模式与专业Agent协作
3. **并行执行**：使用`asyncio.gather`并发执行任务
4. **RAG检索增强**：报告向量化存储与语义检索
5. **LLM工具使用**：DuckDuckGo搜索作为信息检索工具
6. **会话管理**：有状态的多轮对话交互
7. **意图检测**：基于规则和模式匹配的用户意图分类

## 开源协议

Apache License 2.0 - 详见 [LICENSE](LICENSE)

## 贡献

欢迎提交Pull Request！