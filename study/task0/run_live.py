"""Run the official Chapter 1 agent with a verifiable calculator task."""
import json
import os
import re
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "chapter1/context"))
from agent import ContextAwareAgent, ContextMode

task = "请必须调用 calculate 工具计算 (137 * 29) + (864 / 12)，再根据工具返回的结果用中文回答。不要只心算。"
agent = ContextAwareAgent(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    provider="dashscope",
    model="qwen-plus",
    context_mode=ContextMode.FULL,
    verbose=False,
)
agent.client = agent.client.with_options(max_retries=0)
print(f"Provider: {agent.provider}; model: {agent.model}; endpoint: {agent.base_url}", flush=True)
print(f"Task: {task}", flush=True)
result = agent.execute_task(task, max_iterations=3)
result["trajectory"] = asdict(result["trajectory"])
result["task"] = task
result["recorded_at"] = datetime.now().astimezone().isoformat()
calls = result["trajectory"]["tool_calls"]
checks = {
    "terminal_response": bool(result.get("completed")),
    "calculator_returned_4045": any(
        c["tool_name"] == "calculate" and c["result"].get("result") == 4045
        for c in calls
    ),
    "answer_contains_4045": bool(re.search(r"(?<!\d)4,?045(?!\d)", result.get("final_answer") or "")),
    "tool_result_returned_to_model": any(
        m.get("role") == "tool" and '4045' in str(m.get("content", ""))
        for turn in result["trajectory"]["api_turns"]
        for m in turn.get("request", {}).get("messages", [])
    ),
}
result["verification"] = checks
result["task_success"] = all(checks.values())
payload = json.dumps(result, ensure_ascii=False, indent=2, default=str)
assert os.environ["DASHSCOPE_API_KEY"] not in payload
(ROOT / "study/task0/live-result.json").write_text(payload + "\n")
for call in calls:
    print("Tool:", call["tool_name"], call["arguments"], "=>", call["result"])
print("Answer:", result.get("final_answer"))
print("Checks:", json.dumps(checks, ensure_ascii=False))
print("PASS" if result["task_success"] else "FAILED")
sys.exit(0 if result["task_success"] else 1)
