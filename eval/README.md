# 评估

此目录用于后续保存 Agent 测试用例、期望结果和运行记录。

当前阶段验收：

1. 在 Conda `ai_agent` 环境中执行 `python hello_llm.py`，终端打印真实模型回复。
2. 执行 `python hello_llm.py --check-tools`，确认模型实际返回工具调用并在接收工具结果后回复。
3. 执行 `git check-ignore .env`，确认本地 Key 文件被忽略。
