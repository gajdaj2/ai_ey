"""Tymczasowy smoke test — budowa agentów bez wywołań API."""
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

import tools

m = ChatOpenAI(model="gpt-4o-mini", temperature=0)

create_agent(
    m,
    tools=tools.BASIC_TOOLS,
    middleware=[SummarizationMiddleware(model="gpt-4o-mini", trigger=("messages", 6), keep=("messages", 2))],
    checkpointer=InMemorySaver(),
)
print("01 summarization OK")

create_agent(
    m,
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware("ip", strategy="hash", apply_to_input=True),
    ],
)
print("02 pii OK")

mw: list[AgentMiddleware[Any, Any, Any]] = [
    ModelCallLimitMiddleware(thread_limit=4, run_limit=4, exit_behavior="end"),
    ToolCallLimitMiddleware(tool_name="calculator", run_limit=2, exit_behavior="end"),
]
create_agent(m, tools=[tools.calculator], middleware=mw, checkpointer=InMemorySaver())
print("03 limits OK")

create_agent(
    m,
    tools=tools.EMAIL_TOOLS,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "read_email": False,
            }
        )
    ],
    checkpointer=InMemorySaver(),
)
print("04 hitl OK")

create_agent(
    m,
    tools=[tools.unstable_api],
    middleware=[ToolRetryMiddleware(max_retries=3, initial_delay=0.5, backoff_factor=2.0, jitter=False)],
)
print("05 retry OK")

mw2: list[AgentMiddleware[Any, Any, Any]] = [
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    SummarizationMiddleware(model="gpt-4o-mini", trigger=("messages", 8), keep=("messages", 3)),
    ModelCallLimitMiddleware(thread_limit=8, run_limit=6, exit_behavior="end"),
    ToolRetryMiddleware(max_retries=3, initial_delay=0.5, jitter=False),
]
create_agent(m, tools=[*tools.BASIC_TOOLS, tools.unstable_api], middleware=mw2, checkpointer=InMemorySaver())
print("06 combined OK")
print("ALL CONSTRUCTION TESTS PASSED")
