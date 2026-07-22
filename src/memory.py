import json
import re
from pathlib import Path
from typing import Optional

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.client import create_client, create_llm

# Default window size for stretch goal: keep only the last N messages.
DEFAULT_MAX_MESSAGES = 20

# JSON session files live here (stretch: session persistence).
MEMORY_DIR = Path(__file__).resolve().parents[1] / "data" / "sessions"

# Global memory store
memory_store = {}


def _safe_session_filename(session_id):
    """Turn a session id into a safe JSON filename stem."""
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", session_id.strip())
    return safe or "default"


def session_file_path(session_id):
    """Return the JSON path for a session id."""
    return MEMORY_DIR / f"{_safe_session_filename(session_id)}.json"


def _message_to_dict(message):
    return {"type": message.type, "content": message.content}


def _message_from_dict(item):
    msg_type = item.get("type", "human")
    content = item.get("content", "")
    if msg_type in ("ai", "assistant"):
        return AIMessage(content=content)
    if msg_type == "system":
        return SystemMessage(content=content)
    return HumanMessage(content=content)


class LimitedChatMessageHistory(InMemoryChatMessageHistory):
    """In-memory history that keeps only the last ``max_messages`` entries."""

    max_messages: int = DEFAULT_MAX_MESSAGES
    session_id: Optional[str] = None
    persist: bool = False

    def add_message(self, message):
        """Add a message, trim, then optionally persist to JSON."""
        super().add_message(message)
        self.trim()
        if self.persist and self.session_id:
            save_session_to_json(self.session_id, self)

    def trim(self):
        """Keep only the last ``max_messages`` messages."""
        if self.max_messages is not None and len(self.messages) > self.max_messages:
            self.messages[:] = self.messages[-self.max_messages:]


def save_session_to_json(session_id, history=None):
    """Save a session's messages to a JSON file."""
    if history is None:
        history = memory_store.get(session_id)
    if history is None:
        return None

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    path = session_file_path(session_id)
    payload = {
        "session_id": session_id,
        "max_messages": getattr(history, "max_messages", DEFAULT_MAX_MESSAGES),
        "messages": [_message_to_dict(m) for m in history.messages],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_session_from_json(session_id, max_messages=None, persist=True):
    """Load a session from JSON if the file exists; otherwise return None."""
    path = session_file_path(session_id)
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    limit = max_messages
    if limit is None:
        limit = data.get("max_messages", DEFAULT_MAX_MESSAGES)

    history = LimitedChatMessageHistory(
        max_messages=limit,
        session_id=session_id,
        persist=persist,
    )
    # Load without re-saving on every add during hydration.
    history.persist = False
    for item in data.get("messages", []):
        history.add_message(_message_from_dict(item))
    history.persist = persist
    history.trim()
    return history


def get_session_history(session_id, max_messages=None, persist=None):
    """Get or create memory for a session.

    Loads from JSON on first access when a saved file exists.

    ``persist`` defaults to True for new sessions. When LangChain calls this
    with only ``session_id``, existing session persist flags are left alone.
    """
    if session_id not in memory_store:
        use_persist = True if persist is None else persist
        limit = DEFAULT_MAX_MESSAGES if max_messages is None else max_messages
        loaded = load_session_from_json(
            session_id,
            max_messages=limit,
            persist=use_persist,
        )
        if loaded is not None:
            memory_store[session_id] = loaded
        else:
            memory_store[session_id] = LimitedChatMessageHistory(
                max_messages=limit,
                session_id=session_id,
                persist=use_persist,
            )
    else:
        history = memory_store[session_id]
        if max_messages is not None and isinstance(history, LimitedChatMessageHistory):
            history.max_messages = max_messages
            history.trim()
            if history.persist:
                save_session_to_json(session_id, history)
        if isinstance(history, LimitedChatMessageHistory):
            history.session_id = session_id
            if persist is not None:
                history.persist = persist
    return memory_store[session_id]


def clear_session(session_id, delete_file=True):
    """Clear memory for a session (and delete its JSON file by default)."""
    if session_id in memory_store:
        del memory_store[session_id]
    if delete_file:
        path = session_file_path(session_id)
        if path.exists():
            path.unlink()


def build_memory_chatbot():
    """Build a chatbot with conversation memory."""
    client = create_client()
    llm = create_llm(client)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Remember what the user tells you."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )


def chat_with_memory(message, session_id="default", max_messages=None, persist=True):
    """Chat with memory-enabled bot.

    Args:
        message: User message.
        session_id: Session key for conversation history.
        max_messages: Optional max history size (last N messages kept).
        persist: When True, load/save this session as JSON under data/sessions/.
    """
    get_session_history(session_id, max_messages=max_messages, persist=persist)

    chatbot = build_memory_chatbot()
    config = {"configurable": {"session_id": session_id}}
    response = chatbot.invoke({"input": message}, config=config)

    # Ensure final state is written even if history callbacks skipped a save.
    history = memory_store.get(session_id)
    if persist and history is not None:
        if isinstance(history, LimitedChatMessageHistory):
            history.persist = True
            history.session_id = session_id
        save_session_to_json(session_id, history)

    return response.content
