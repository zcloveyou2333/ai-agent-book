# Task0 Agent 基础与环境准备

学习范围：Chapter 1 AI Agent 入门。截止时间：2026 年 10 月 12 日 24:00（北京时间）。

本次完成 Python 环境和第一章依赖安装，先运行官方离线基础演示并通过 3 项测试，再使用百炼 `qwen-plus` 跑通第一章 `context` 的真实工具调用闭环。真实实验在 2026 年 10 月 13 日 00:00:47 完成，晚于公告中的 Task0 截止时间；是否接受补交以课程方为准。

## Agent 理解与学习笔记

AI Agent 是围绕目标持续采取行动、读取结果并调整下一步的系统。核心框架可以理解为 Agent = LLM + Context + Tools：LLM 负责理解需求、规划和选择动作；Context 是当前决策所依据的信息，包括系统指令、用户需求、历史消息、工具定义和工具执行结果；Tools 提供读取文件、搜索信息、执行代码等与外部环境交互的能力。

三个组件通过 ReAct 循环协同工作：模型根据上下文提出行动，程序执行工具，把结果追加到上下文，再让模型决定继续行动还是结束。工具调用请求不等于工具执行成功，最终回答也不等于任务正确完成，因此需要检查实际输出和验证结果。文件、网页等属于外部环境，只有读取后进入上下文的信息才能成为模型当轮决策的依据。

本次运行第一章的离线搜索演示，观察到两轮“思考、行动、观察”和一次最终回答，共 7 步轨迹。第一轮示范查询概念，第二轮补充适用场景，最后综合答案。这让我理解到，Agent 的价值来自决策、信息和行动形成闭环。这里的思考文本、工具调用及搜索结果均为教学预设，只能说明控制流程，不能证明真实模型已经联网，也不能据此得出缓存性能结论。

随后使用百炼 qwen-plus 跑通第一章真实 Agent 实验：模型首先调用 calculate 计算 (137×29)+(864÷12)，本地工具返回 4045.0，再把工具结果送回模型，得到正确回答。两次 API 请求均成功，验证了模型决策、工具执行、观测回传和最终回答的完整闭环。这也说明必须区分示例回放、真实请求成功和任务结果正确，不能仅凭程序有输出就认定实验完成。

## 扩展分析 Codex

Codex 是我当前使用的编程助手。官方文档说明其可以读取、修改并运行本地代码；下面按课程框架分析本次任务中的实际使用方式。[官方说明](https://learn.chatgpt.com/docs/codex/cli)

| 组件 | 在本次任务中的对应内容 |
| --- | --- |
| LLM | 理解 Task0 要求，选择实验，解释安装失败并决定下一步操作的模型。产品名称并不等同于某个固定模型型号。 |
| Context | 课程要求、读取到的 README 和 Python 源码、安装日志、实验输出与测试结果。磁盘上尚未读取的所有文件并不会自动成为上下文。 |
| Tools | 搜索和读取文件、执行安装命令与 Python 实验、运行测试、写入学习记录等接口。 |

一个实际闭环是：安装依赖时得到 403 错误 → 把错误作为观察 → 调整为从 PyPI 解析安装 → 运行实验和测试确认环境能工作。这里既需要模型作判断，也需要工具实际执行，并依赖上下文保留失败原因。

## 环境与复现

- 平台：macOS Apple Silicon。
- Python：3.13.12，使用项目独立的 `.venv`，符合教程要求的 3.11–3.13。
- 源码版本：`dbc046eb896ac4e39aa19c7774c8bf49583b89a6`。
- 使用浅克隆和稀疏检出，当前包含共享包、第一章搜索实验及书稿；其他实验可按需检出。
- `uv sync --locked --extra ch1` 因锁文件中的镜像资源返回 403 未成功；改为安装 `.[ch1]`，实际版本见 `requirements-resolved.txt`。本次没有声称复现官方锁定环境。

在仓库根目录运行：

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python --index-url https://pypi.org/simple -e '.[ch1]' pytest
.venv/bin/python chapter1/web-search-agent/main.py --provider offline-demo --output study/task0/offline-demo.json
.venv/bin/python -m pytest chapter1/web-search-agent/tests/test_offline_demo.py -q
```

运行产物：`run.txt` 是原始输出，`offline-demo.json` 保存完整轨迹，`tests.txt` 保存测试结果，`environment.json` 保存不含密钥的环境信息。

## LLM API 配置与真实实验

已将百炼兼容接口配置为教程读取的 `DASHSCOPE_BASE_URL` 和 `DASHSCOPE_API_KEY`，密钥保存在 Git 忽略的本地 `.env` 中。模型选择 `qwen-plus`。

```bash
.venv/bin/python study/task0/run_live.py
```

脚本复用第一章 `context/agent.py` 的 `ContextAwareAgent`，使用完整上下文，最多 3 轮。任务要求调用 `calculate` 计算 `(137 * 29) + (864 / 12)`。第一轮模型发出工具调用，本地计算器返回 `4045.0`；第二轮请求包含工具结果，模型最终回答 `4045.0`。两次请求均为 HTTP 200，无重试或备用服务。

核验检查了终止回答、工具数值、答案数值以及后续请求确实携带工具观测，4 项均通过。这是第一章单任务基础实验，不等于全部消融实验，也不是实时搜索实验。`live-run.txt` 保存输出，`live-result.json` 保存无凭据的请求与响应。

## 环境运行截图

真实模型实验使用百炼 qwen-plus，完成模型决策、计算器执行、工具结果回传和最终回答。以下截图展示本机运行记录页中的实际输出。

![真实模型与工具调用实验](images/live-run.png)

离线环境与基础演示记录如下；离线示例不调用真实模型。

![离线实验环境](images/offline-environment.png)

![离线演示与测试结果](images/offline-run.png)

[打卡心得纯文本](check-in.txt) · [真实实验原始输出](live-run.txt) · [真实请求与响应](live-result.json) · [实验脚本](run_live.py)

## 参考资料

- [Chapter 1 正文](https://github.com/bojieli/ai-agent-book/blob/dbc046eb896ac4e39aa19c7774c8bf49583b89a6/book/chapter1.md)
- [第一章搜索实验说明](https://github.com/bojieli/ai-agent-book/blob/dbc046eb896ac4e39aa19c7774c8bf49583b89a6/chapter1/web-search-agent/README.md)
- [打卡表单](https://magicyang.feishu.cn/share/base/form/shrcnCXBWW7pd3HG4yHUjwaGYYx)
