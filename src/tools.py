from datetime import datetime
from pathlib import Path
import fnmatch
import re

from langchain_core.tools import StructuredTool, Tool
from pydantic import BaseModel, Field

# Skip heavy / generated trees when searching the project.
_SKIP_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".agents",
}

# Q Branch lookup tables — deterministic, not random.
_MONTH_CALLSIGNS = {
    1: "Wolf",
    2: "Fox",
    3: "Viper",
    4: "Hawk",
    5: "Panther",
    6: "Falcon",
    7: "Cobra",
    8: "Raven",
    9: "Jaguar",
    10: "Shark",
    11: "Eagle",
    12: "Lynx",
}

_COLOR_CODES = {
    "blue": "Cobalt",
    "red": "Crimson",
    "green": "Emerald",
    "emerald": "Emerald",
    "black": "Shadow",
    "white": "Ghost",
    "gold": "Aurum",
    "silver": "Chrome",
    "purple": "Violet",
    "orange": "Amber",
    "yellow": "Solar",
    "pink": "Rose",
    "brown": "Umber",
    "gray": "Steel",
    "grey": "Steel",
    "teal": "Tide",
    "navy": "Deepsea",
    "cyan": "Ice",
    "magenta": "Fuchsia",
    "maroon": "Garnet",
}


def calculator(expression):
    """Safely evaluate a math expression."""
    try:
        allowed = set('0123456789+-*/.()')
        clean = expression.replace(' ', '')
        if not set(clean).issubset(allowed):
            return "Error: Only basic math operations allowed"
        return f"Result: {eval(clean)}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_time(format_type="default"):
    """Get current time in various formats."""
    now = datetime.now()
    formats = {
        "short": now.strftime("%H:%M"),
        "long": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "default": now.strftime("%B %d, %Y at %I:%M %p")
    }
    return formats.get(format_type, formats["default"])


def word_counter(text):
    """Count words and characters in text."""
    words = len(text.split())
    chars = len(text)
    return f"Words: {words}, Characters: {chars}"


def search_files(pattern="*"):
    """Search for files under the current working directory.

    Args:
        pattern: Glob (``*.py``) or substring (``memory``). Use ``*`` for all files.
    """
    cwd = Path.cwd().resolve()
    pattern = (pattern or "*").strip()
    matches = []

    try:
        for path in cwd.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            rel = path.relative_to(cwd).as_posix()
            name = path.name
            if (
                fnmatch.fnmatch(name, pattern)
                or fnmatch.fnmatch(rel, pattern)
                or (pattern != "*" and pattern in rel)
            ):
                matches.append(rel)
    except Exception as e:
        return f"Error: {str(e)}"

    matches = sorted(matches)
    total = len(matches)
    shown = matches[:50]
    if total == 0:
        return f"No files matching '{pattern}' under {cwd}"

    lines = [
        f"Found {total} file(s) under {cwd} matching '{pattern}':",
        *[f"- {item}" for item in shown],
    ]
    if total > len(shown):
        lines.append(f"... and {total - len(shown)} more")
    return "\n".join(lines)


# Create LangChain Tool wrappers
calc_tool = Tool(
    name="Calculator",
    description="Perform basic math. Input: expression like '25 * 4'",
    func=calculator
)

time_tool = Tool(
    name="CurrentTime",
    description="Get current time. Input: 'short', 'long', 'date', or 'default'",
    func=get_time
)

word_tool = Tool(
    name="WordCounter",
    description="Count words and characters. Input: text to analyze",
    func=word_counter
)

file_search_tool = Tool(
    name="FileSearch",
    description=(
        "Search files in the current directory. "
        "Input: glob like '*.py' or substring like 'memory'"
    ),
    func=search_files
)


def _parse_birthdate(birthdate):
    """Parse birthdate string into a datetime (date-only)."""
    text = str(birthdate).strip()
    if not text:
        raise ValueError("Birthdate is required")

    # Already ISO-ish from Streamlit date_input
    for fmt in (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    # Digits only: YYYYMMDD
    digits = re.sub(r"\D", "", text)
    if len(digits) == 8:
        return datetime.strptime(digits, "%Y%m%d")

    raise ValueError(
        "Could not parse birthdate. Try YYYY-MM-DD (e.g. 1985-07-21)."
    )


def forge_spy_codename(name: str, birthdate: str, favorite_color: str) -> str:
    """Assign a deterministic secret spy codename.

    Combines operative name, birthdate, and favorite color into a
    Bond-style callsign. Same inputs always yield the same codename.
    """
    name = (name or "").strip()
    favorite_color = (favorite_color or "").strip()
    if not name:
        return "Error: Operative name is required"
    if not favorite_color:
        return "Error: Favorite color is required"

    try:
        born = _parse_birthdate(birthdate)
    except ValueError as e:
        return f"Error: {e}"

    parts = name.split()
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else parts[0]
    initials = "".join(p[0] for p in parts if p).upper()

    color_key = favorite_color.lower().strip()
    color_code = _COLOR_CODES.get(color_key)
    if color_code is None:
        # Allow phrases like "dark blue" / "emerald green"
        for key, val in _COLOR_CODES.items():
            if key in color_key:
                color_code = val
                break
    if color_code is None:
        # Unknown color → sanitize to a single callsign token
        color_code = re.sub(r"[^A-Za-z]", "", favorite_color).title() or "Unknown"

    animal = _MONTH_CALLSIGNS[born.month]
    day_tag = f"{born.day:02d}"
    year_tag = f"{born.year % 100:02d}"

    # Clearance flavor from a stable hash of the dossier (not crypto).
    seed = sum(ord(c) for c in f"{name.lower()}|{born.date()}|{color_key}")
    clearance = ["RESTRICTED", "SECRET", "TOP SECRET", "EYES ONLY"][seed % 4]
    designation = f"{initials}-{year_tag}"

    return (
        f"CLASSIFIED ({clearance})\n"
        f"Operative: {name}\n"
        f"Codename: {color_code.upper()} {animal.upper()}-{day_tag}\n"
        f"Callsign: {designation}\n"
        f"Dossier: born {born.strftime('%Y-%m-%d')}, "
        f"color preference '{favorite_color}', "
        f"surname fragment '{last[:3].upper()}' / given '{first[:3].upper()}'\n"
        f"(Same inputs always produce this codename — Q Branch guarantee.)"
    )


class SpyCodenameInput(BaseModel):
    """Schema for the SpyCodenameGenerator tool."""

    name: str = Field(description="Full name of the operative")
    birthdate: str = Field(
        description="Birthdate, preferably YYYY-MM-DD (also accepts MM/DD/YYYY)"
    )
    favorite_color: str = Field(description="Favorite color (e.g. blue, crimson)")


codename_tool = StructuredTool.from_function(
    func=forge_spy_codename,
    name="SpyCodenameGenerator",
    description=(
        "Generate a secret spy codename from an operative's name, birthdate, "
        "and favorite color. Always call this tool when the user wants a "
        "codename, callsign, or spy identity assigned. "
        "Requires name, birthdate, and favorite_color."
    ),
    args_schema=SpyCodenameInput,
)


def get_all_tools():
    """Return list of all available tools."""
    return [
        calc_tool,
        time_tool,
        word_tool,
        file_search_tool,
        codename_tool,
    ]


def get_special_agent_tools():
    """Tools for the Special Agent (Q Branch) desk."""
    return [codename_tool]
