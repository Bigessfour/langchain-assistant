"""Special Agent desk: Q Branch spy codename assignment (stretch)."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.client import create_client, create_llm
from src.tools import get_special_agent_tools

_checkpointer = MemorySaver()
_agent = None

SYSTEM_PROMPT = (
    "You are Q, head of Q Branch, assigning secret spy identities. "
    "When an operative needs a codename, callsign, or spy identity, "
    "you MUST call the SpyCodenameGenerator tool with their name, "
    "birthdate, and favorite color — never invent a codename yourself. "
    "If any of those three fields is missing, ask for it before calling the tool. "
    "After the tool returns, present the CLASSIFIED dossier clearly and "
    "with a dry British wit. Keep conversation memory for this thread."
)


def _extract_text(content):
    """Normalize Nova / Bedrock message content to a plain string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    parts.append(str(block["text"]))
                elif block.get("type") == "reasoning_content":
                    continue
                elif "text" in block and isinstance(block["text"], str):
                    parts.append(block["text"])
            else:
                text = getattr(block, "text", None)
                if text:
                    parts.append(str(text))
        return "\n".join(p.strip() for p in parts if p and str(p).strip()).strip()
    return str(content).strip()


def build_special_agent(force_rebuild=False):
    """Build (or reuse) the Q Branch special agent."""
    global _agent
    if _agent is not None and not force_rebuild:
        return _agent

    client = create_client()
    llm = create_llm(client)
    _agent = create_agent(
        model=llm,
        tools=get_special_agent_tools(),
        system_prompt=SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )
    return _agent


def chat_with_special_agent(message, session_id="special-agent"):
    """Send a message to the Special Agent (memory + SpyCodenameGenerator)."""
    agent = build_special_agent()
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )
    messages = result.get("messages", [])
    tools_used = []
    for msg in messages:
        name = type(msg).__name__
        if name == "ToolMessage":
            tools_used.append(getattr(msg, "name", None) or "tool")
        tool_calls = getattr(msg, "tool_calls", None) or []
        for call in tool_calls:
            if isinstance(call, dict) and call.get("name"):
                tools_used.append(call["name"])

    reply = ""
    if messages:
        reply = _extract_text(getattr(messages[-1], "content", ""))

    seen = set()
    unique_tools = []
    for name in tools_used:
        if name and name not in seen:
            seen.add(name)
            unique_tools.append(name)

    return {"reply": reply or "(no text response)", "tools_used": unique_tools}


def reset_special_agent():
    """Drop the cached agent so the next call rebuilds it."""
    global _agent
    _agent = None
