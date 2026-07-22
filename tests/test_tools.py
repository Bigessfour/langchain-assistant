from src.tools import (
    calculator,
    forge_spy_codename,
    get_all_tools,
    get_time,
    search_files,
    word_counter,
)


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


def test_search_files_glob(tmp_path, monkeypatch):
    """Stretch: file search finds files by glob in cwd."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
    (tmp_path / "app.py").write_text("print(1)", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "helper.py").write_text("x", encoding="utf-8")

    result = search_files("*.py")
    assert "Found 2 file(s)" in result
    assert "app.py" in result
    assert "nested/helper.py" in result
    assert "notes.txt" not in result


def test_search_files_substring(tmp_path, monkeypatch):
    """Stretch: file search finds files by substring."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory_notes.md").write_text("mem", encoding="utf-8")
    (tmp_path / "other.txt").write_text("x", encoding="utf-8")

    result = search_files("memory")
    assert "memory_notes.md" in result
    assert "other.txt" not in result


def test_search_files_no_match(tmp_path, monkeypatch):
    """Stretch: file search reports when nothing matches."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    result = search_files("*.xyz")
    assert "No files matching" in result


def test_forge_spy_codename_deterministic():
    """Same dossier always yields the same secret codename."""
    a = forge_spy_codename("Stephen McKitrick", "1985-07-21", "blue")
    b = forge_spy_codename("Stephen McKitrick", "1985-07-21", "blue")
    assert a == b
    assert "COBALT" in a
    assert "COBRA-21" in a
    assert "SM-85" in a
    assert "CLASSIFIED" in a


def test_forge_spy_codename_color_phrase():
    """Color phrases still map to a known code."""
    result = forge_spy_codename("Jane Doe", "1990-03-15", "dark blue")
    assert "COBALT" in result
    assert "VIPER-15" in result


def test_forge_spy_codename_rejects_bad_date():
    """Invalid birthdate returns an error string."""
    result = forge_spy_codename("Agent", "not-a-date", "red")
    assert "Error" in result


def test_get_all_tools_returns_list():
    """Test that get_all_tools returns a list."""
    tools = get_all_tools()
    assert isinstance(tools, list)
    assert len(tools) == 5
    names = {tool.name for tool in tools}
    assert "FileSearch" in names
    assert "SpyCodenameGenerator" in names


def test_tools_have_names():
    """Test that all tools have names."""
    tools = get_all_tools()
    for tool in tools:
        assert hasattr(tool, 'name')
        assert len(tool.name) > 0
