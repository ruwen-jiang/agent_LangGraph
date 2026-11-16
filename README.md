# AI Agent 起步项目

使用独立 Conda 环境连接支持 Tool Calling 的模型，为后续 Agent、工具、评估和界面提供基础。

**Agent 最小循环是决策→执行工具→观察→再决策**

## 目录

```text
agent/           Agent 决策、状态和执行循环
tools/           可调用工具
eval/            评估用例和运行记录
app/             后续 FastAPI / Streamlit 入口
hello_llm.py     发送消息并打印模型回复；可选 Tool Calling 检查
environment.yml Conda 环境定义
requirements.txt Python 依赖
.env.example     配置模板，可提交
.env             本地 API Key，Git 忽略
```

## 1. 创建 Conda 环境

要求 Python 3.11+；本项目使用 Python 3.11 以兼容全部依赖。所有依赖安装在 `ai_agent` 中。

```powershell
conda create -n ai_agent python=3.11 pip -y
conda activate ai_agent
python -m pip install -r requirements.txt
```

也可在项目根目录运行 `conda env create -f environment.yml` 一次创建环境并安装依赖。

本机 Conda 安装于 `D:\software\conda`；安装目录需要管理员写权限，因此使用 Conda 默认用户环境位置 `C:\Users\Admin\.conda\envs\ai_agent`。这是独立的 Conda 环境。若终端尚未识别 `conda`，可使用完整路径：

```powershell
& 'D:\software\conda\Scripts\conda.exe' create --prefix 'C:\Users\Admin\.conda\envs\ai_agent' python=3.11 pip -y
& 'C:\Users\Admin\.conda\envs\ai_agent\python.exe' -m pip install -r requirements.txt
& 'C:\Users\Admin\.conda\envs\ai_agent\python.exe' hello_llm.py
```

若要在 PowerShell 中使用 `conda activate ai_agent`，先运行 `& 'D:\software\conda\Scripts\conda.exe' init powershell`，然后重新打开终端。

验证 Python 版本及环境路径：

```powershell
python --version
python -c "import sys; print(sys.executable); print(sys.prefix)"
python -m pip check
```

应看到 Python 3.11.x 和 `ai_agent` 环境路径。

依赖包括 `openai`、`langgraph`、`langchain`、`chromadb`、`fastapi`、`streamlit`、`python-dotenv`、`requests`。

## 2. 申请模型 API 并配置 Key

默认使用 DeepSeek 的 OpenAI 兼容 API。当前官方文档中的 `deepseek-flash` 支持 Tool Calling，参见 [模型列表](https://api-docs.deepseek.com/quick_start/pricing) 和 [工具调用文档](https://api-docs.deepseek.com/guides/tool_calls)。

1. 在 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册、登录，并确认账户可调用 API。
2. 在 [API Keys 页面](https://platform.deepseek.com/api_keys) 创建自己的 API Key。
3. 如项目尚无 `.env`，复制 `.env.example` 为 `.env`；已有 `.env` 时直接编辑，保留自己的配置。
4. 将真实 Key 填入本地 `.env` 的 `OPENAI_API_KEY`。

```dotenv
OPENAI_API_KEY=在此填写自己的真实Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-flash
```

也可以使用其他支持 Tool Calling 的 OpenAI 兼容服务；Key、地址、模型名必须属于同一服务：

| 服务 | OPENAI_BASE_URL | OPENAI_MODEL 示例 |
| --- | --- | --- |
| DeepSeek | https://api.deepseek.com | deepseek-flash |
| 阿里云百炼 Qwen（中国内地） | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus |
| OpenAI | https://api.openai.com/v1 | gpt-4o-mini |

Qwen 地址需与账号地域一致；模型可用性以对应服务控制台为准。

脚本从自身所在目录读取 `.env`。进程中已设置的同名环境变量优先。脚本不会打印 API Key，API 失败时仅输出状态和排查提示。

## 3. 验证模型回复

在 `ai_agent` 环境、项目根目录执行：

```powershell
python hello_llm.py
python hello_llm.py "请用一句话说明什么是 AI Agent。"
```

验收条件：命令退出码为 0，终端打印真实 API 返回的模型回复。缺少 Key 时会输出配置提示并返回退出码 2，不会伪造模型回复。

可选：实际验证工具调用完整过程（会请求模型两次）：

```powershell
python hello_llm.py --check-tools
```

脚本要求模型调用 `add_numbers`，本地执行加法，将结果作为工具观察发回模型，然后打印最终回复。只有收到实际 `tool_calls` 才会执行工具。

## 4. Git 与 GitHub

`.gitignore` 忽略 `.env`、`.env.*`、Python 缓存、虚拟环境及本地向量库，同时允许提交 `.env.example`。

```powershell
git check-ignore .env
git ls-files .env
```

前者应输出 `.env`；后者应无输出。

本地首次初始化：

```powershell
git init -b main
git add .
git commit -m "Initialize AI agent project"
```

GitHub 需要自己的账户授权。若已安装并登录 GitHub CLI，可从根目录创建私有仓库并推送：

```powershell
gh auth login
gh repo create agent --private --source=. --remote=origin --push
```

也可在 [GitHub 新建仓库页面](https://github.com/new) 创建名为 `agent` 的空仓库，再按页面提示配置 `origin` 并推送。

## 阶段验收

- [x] `ai_agent` Conda 环境使用 Python 3.11.18，八项依赖均已安装、从环境内导入，`pip check` 通过。
- [ ] 执行 `python hello_llm.py`，终端打印真实模型回复。
- [x] GitHub 仓库 [ruwen-jiang/agent_LangGraph](https://github.com/ruwen-jiang/agent_LangGraph) 已创建，项目已推送至 `main`。
- [x] 项目骨架和 README 初稿已提供。
- [x] 本地 `.env` 被忽略，提交中仅保留 `.env.example` 模板。
- [x] 已写下：Agent 最小循环是决策→执行工具→观察→再决策。

环境安装和真实 API 调用是独立的验收项。没有有效 Key 或 GitHub 授权时，对应项保持未完成。

2026-11-16 本机验证：Python 3.11.18；八项依赖均从 `ai_agent` 环境导入；`python -m pip check` 通过。已使用本地 Key 发出真实 API 请求，但服务返回 HTTP 402；按 [DeepSeek 错误码说明](https://api-docs.deepseek.com/quick_start/error_codes)，该状态表示余额不足。用户选择暂缓模型验收；充值或更换可用 API 配置后，应重新运行普通回复和 Tool Calling 检查。
