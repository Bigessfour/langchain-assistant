from src.tools import calculator, get_all_tools, get_time, word_counter


def test_calculator_addition():
    """Test calculator with addition."""
    result = calculator("2 + 3")
    assert "5" in result


def test_calculator_multiplication():
    """Test calculator with multiplication."""
    result = calculator("4 * 5")
    assert "20" in result


def test_calculator_rejects_invalid():
    """Test calculator rejects non-math input."""
    result = calculator("hello")
    assert "Error" in result


def test_get_time_returns_string():
    """Test that time function returns a string."""
    result = get_time("default")
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_time_formats():
    """Test different time formats."""
    short = get_time("short")
    long = get_time("long")
    assert len(short) < len(long)


def test_word_counter_basic():
    """Test word counter with simple text."""
    result = word_counter("hello world")
    assert "Words: 2" in result


def test_word_counter_characters():
    """Test word counter includes character count."""
    result = word_counter("hello")
    assert "Characters: 5" in result


def test_get_all_tools_returns_list():
    """Test that get_all_tools returns a list."""
    tools = get_all_tools()
    assert isinstance(tools, list)
    assert len(tools) == 3


def test_tools_have_names():
    """Test that all tools have names."""
    tools = get_all_tools()
    for tool in tools:
        assert hasattr(tool, 'name')
        assert len(tool.name) > 0
