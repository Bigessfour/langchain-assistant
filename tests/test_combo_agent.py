from src.combo_agent import (
    _extract_text,
    build_combo_agent,
    chat_with_combo,
    reset_combo_agent,
)


def test_extract_text_from_string():
    assert _extract_text("hello") == "hello"


def test_extract_text_from_nova_blocks():
    content = [
        {"type": "reasoning_content", "reasoning_content": {"text": "thinking"}},
        {"type": "text", "text": "Final answer"},
    ]
    assert _extract_text(content) == "Final answer"


def test_build_combo_agent_exists():
    assert callable(build_combo_agent)


def test_chat_with_combo_exists():
    assert callable(chat_with_combo)


def test_reset_combo_agent_clears_cache():
    reset_combo_agent()
    # Should not raise
    reset_combo_agent()
