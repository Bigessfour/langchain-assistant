from langchain_core.messages import AIMessage, HumanMessage

from src.memory import (
    DEFAULT_MAX_MESSAGES,
    LimitedChatMessageHistory,
    clear_session,
    get_session_history,
    load_session_from_json,
    memory_store,
    save_session_to_json,
    session_file_path,
)


def test_get_session_history_creates_new():
    """Test that new sessions get fresh memory."""
    clear_session("test_new")
    history = get_session_history("test_new", persist=False)
    assert history is not None
    assert len(history.messages) == 0


def test_get_session_history_returns_same():
    """Test that same session returns same memory."""
    clear_session("test_same")
    history1 = get_session_history("test_same", persist=False)
    history2 = get_session_history("test_same", persist=False)
    assert history1 is history2


def test_different_sessions_separate():
    """Test that different sessions have separate memory."""
    clear_session("session_a")
    clear_session("session_b")
    history_a = get_session_history("session_a", persist=False)
    history_b = get_session_history("session_b", persist=False)
    assert history_a is not history_b


def test_clear_session():
    """Test that clearing session removes memory."""
    get_session_history("test_clear", persist=False)
    assert "test_clear" in memory_store
    clear_session("test_clear")
    assert "test_clear" not in memory_store


def test_build_memory_chatbot_exists():
    """Test that the chatbot builder exists."""
    from src.memory import build_memory_chatbot
    assert callable(build_memory_chatbot)


def test_session_uses_limited_history():
    """New sessions should use LimitedChatMessageHistory."""
    clear_session("test_limited_type")
    history = get_session_history("test_limited_type", persist=False)
    assert isinstance(history, LimitedChatMessageHistory)
    assert history.max_messages == DEFAULT_MAX_MESSAGES


def test_memory_keeps_only_last_n_messages():
    """Stretch: history trims to the last N messages."""
    clear_session("test_trim")
    history = get_session_history("test_trim", max_messages=4, persist=False)

    for i in range(3):
        history.add_message(HumanMessage(content=f"user-{i}"))
        history.add_message(AIMessage(content=f"bot-{i}"))

    assert len(history.messages) == 4
    assert history.messages[0].content == "user-1"
    assert history.messages[-1].content == "bot-2"


def test_trim_when_max_messages_lowered():
    """Lowering max_messages on an existing session trims immediately."""
    clear_session("test_lower_limit")
    history = get_session_history("test_lower_limit", max_messages=10, persist=False)
    for i in range(5):
        history.add_message(HumanMessage(content=f"m-{i}"))

    assert len(history.messages) == 5
    get_session_history("test_lower_limit", max_messages=2, persist=False)
    assert len(history.messages) == 2
    assert [m.content for m in history.messages] == ["m-3", "m-4"]


def test_save_and_load_session_json(tmp_path, monkeypatch):
    """Stretch: session messages persist to JSON and reload."""
    monkeypatch.setattr("src.memory.MEMORY_DIR", tmp_path)
    clear_session("persist-demo")

    history = get_session_history("persist-demo", max_messages=10, persist=True)
    history.add_message(HumanMessage(content="My name is Steve"))
    history.add_message(AIMessage(content="Hi Steve"))

    path = session_file_path("persist-demo")
    assert path.exists()

    # Drop in-memory store and reload from disk.
    memory_store.clear()
    loaded = load_session_from_json("persist-demo")
    assert loaded is not None
    assert len(loaded.messages) == 2
    assert loaded.messages[0].content == "My name is Steve"
    assert loaded.messages[1].content == "Hi Steve"


def test_get_session_history_loads_json(tmp_path, monkeypatch):
    """Stretch: get_session_history hydrates from JSON on first access."""
    monkeypatch.setattr("src.memory.MEMORY_DIR", tmp_path)
    clear_session("hydrate-me")

    history = get_session_history("hydrate-me", persist=True)
    history.add_message(HumanMessage(content="remember this"))
    save_session_to_json("hydrate-me", history)

    memory_store.clear()
    restored = get_session_history("hydrate-me", persist=True)
    assert len(restored.messages) == 1
    assert restored.messages[0].content == "remember this"


def test_clear_session_deletes_json(tmp_path, monkeypatch):
    """Stretch: clear_session removes the JSON file."""
    monkeypatch.setattr("src.memory.MEMORY_DIR", tmp_path)
    clear_session("to-delete")

    history = get_session_history("to-delete", persist=True)
    history.add_message(HumanMessage(content="bye"))
    path = session_file_path("to-delete")
    assert path.exists()

    clear_session("to-delete")
    assert "to-delete" not in memory_store
    assert not path.exists()
