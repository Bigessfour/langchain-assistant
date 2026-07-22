"""Combined assistant: conversation memory + tools (stretch goal)."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.client import create_client, create_llm
from src.tools import get_all_tools

# In-process memory for combo agent threads (keyed by session / thread_id).
_checkpointer = MemorySaver()
_agent = None

SYSTEM_PROMPT = (
    "You are a helpful combined assistant with conversation memory and tools. "
    "Remember facts the user shares in this thread. "
    "When a question needs math, the current time, a word/character count, "
    "a file search, or a secret spy codename, call the matching tool "
    "(Calculator, CurrentTime, WordCounter, FileSearch, SpyCodenameGenerator) "
    "instead of guessing. "
    "For SpyCodenameGenerator you need name, birthdate, and favorite_color. "
    "After a tool runs, answer clearly using the tool result."
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


def build_combo_agent(force_rebuild=False):
    """Build (or reuse) a tool-calling agent with a memory checkpointer."""
    global _agent
    if _agent is not None and not force_rebuild:
        return _agent

    client = create_client()
    llm = create_llm(client)
    _agent = create_agent(
        model=llm,
        tools=get_all_tools(),
        system_prompt=SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )
    return _agent


def chat_with_combo(message, session_id="combo-demo"):
    """Send a message to the combo agent (memory + tools).

    Args:
        message: User text.
        session_id: Thread id for LangGraph memory (separate from JSON memory chat).

    Returns:
        dict with reply text and a short list of tools used this turn (if any).
    """
    agent = build_combo_agent()
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
    # Unique tool names, preserve order
    seen = set()
    unique_tools = []
    for name in tools_used:
        if name and name not in seen:
            seen.add(name)
            unique_tools.append(name)

    return {"reply": reply or "(no text response)", "tools_used": unique_tools}


def reset_combo_agent():
    """Drop the cached agent so the next call rebuilds it (tests / hot reload)."""
    global _agent
    _agent = None
