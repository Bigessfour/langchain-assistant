from src.memory import clear_session, get_session_history, memory_store


def test_get_session_history_creates_new():
    """Test that new sessions get fresh memory."""
    clear_session("test_new")
    history = get_session_history("test_new")
    assert history is not None
    assert len(history.messages) == 0


def test_get_session_history_returns_same():
    """Test that same session returns same memory."""
    clear_session("test_same")
    history1 = get_session_history("test_same")
    history2 = get_session_history("test_same")
    assert history1 is history2


def test_different_sessions_separate():
    """Test that different sessions have separate memory."""
    clear_session("session_a")
    clear_session("session_b")
    history_a = get_session_history("session_a")
    history_b = get_session_history("session_b")
    assert history_a is not history_b


def test_clear_session():
    """Test that clearing session removes memory."""
    get_session_history("test_clear")
    assert "test_clear" in memory_store
    clear_session("test_clear")
    assert "test_clear" not in memory_store


def test_build_memory_chatbot_exists():
    """Test that the chatbot builder exists."""
    from src.memory import build_memory_chatbot
    assert callable(build_memory_chatbot)
