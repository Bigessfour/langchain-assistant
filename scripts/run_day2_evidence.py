#!/usr/bin/env python3
"""Run Day 2 testing scenarios one-by-one and write evidence logs.

Usage:
  python scripts/run_day2_evidence.py            # all scenarios
  python scripts/run_day2_evidence.py --offline  # skip Bedrock calls
  python scripts/run_day2_evidence.py 07 08 09   # specific IDs
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"
HUB_EVIDENCE_DIR = Path(
    "/Users/stephenmckitrick/AICO-ECHO/aico-challenges-w13/aico-challenges-w13"
    "/day-2-composability-chains-memory-and-tools/submissions/Bigessfour/evidence"
)

OFFLINE_IDS = {"01", "04", "05", "07", "08", "09", "10", "11"}
BEDROCK_IDS = {"02", "03", "06"}


def write_log(filename: str, body: str, ok: bool) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    HUB_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    status = "PASS" if ok else "FAIL"
    text = f"# {filename}\n# status: {status}\n# captured: {stamp}\n\n{body.rstrip()}\n"
    path = EVIDENCE_DIR / filename
    path.write_text(text, encoding="utf-8")
    hub_path = HUB_EVIDENCE_DIR / filename
    hub_path.write_text(text, encoding="utf-8")
    print(f"[{status}] {filename}")
    return path


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    out = []
    out.append(f"$ {' '.join(cmd)}\n")
    if proc.stdout:
        out.append(proc.stdout)
    if proc.stderr:
        out.append("\n--- stderr ---\n")
        out.append(proc.stderr)
    out.append(f"\nexit_code: {proc.returncode}\n")
    return proc.returncode == 0, "".join(out)


def scenario_01() -> tuple[bool, str]:
    ok, body = run_cmd(["ls", "-la", "src/"])
    needed = {"chains.py", "memory.py", "tools.py", "client.py", "prompts.py"}
    listing = set(body.split())
    missing = sorted(needed - listing)
    if missing:
        body += f"\nMISSING: {missing}\n"
        return False, body
    body += "\nOK: chains.py, memory.py, tools.py present alongside Day 1 files.\n"
    return True, body


def scenario_02() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            from src.chains import generate_and_evaluate

            print("Running generate_and_evaluate('mobile app ideas')...")
            result = generate_and_evaluate("mobile app ideas")
            print("\n=== RESULT ===")
            print(result)
        text = buf.getvalue()
        ok = bool(result) and len(str(result)) > 20
        return ok, text
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_03() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            from src.chains import research_pipeline

            print("Running research_pipeline('renewable energy')...")
            result = research_pipeline("renewable energy")
            print("\n=== KEYS ===")
            print(sorted(result.keys()) if isinstance(result, dict) else type(result))
            if isinstance(result, dict):
                for key in ("research", "outline", "summary"):
                    value = str(result.get(key, ""))
                    print(f"\n--- {key} ({len(value)} chars) ---")
                    print(value[:500])
        keys_ok = (
            isinstance(result, dict)
            and {"research", "outline", "summary"}.issubset(result.keys())
        )
        return keys_ok, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_04() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            from src.memory import clear_session, get_session_history

            clear_session("test")
            h1 = get_session_history("test")
            h2 = get_session_history("test")
            print(f"first call id:  {id(h1)}")
            print(f"second call id: {id(h2)}")
            print(f"same object:    {h1 is h2}")
            print(f"message count:  {len(h1.messages)}")
        return h1 is h2, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_05() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            from src.memory import clear_session, get_session_history

            clear_session("alice")
            clear_session("bob")
            alice = get_session_history("alice")
            bob = get_session_history("bob")
            print(f"alice id: {id(alice)}")
            print(f"bob id:   {id(bob)}")
            print(f"separate: {alice is not bob}")
        return alice is not bob, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_06() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(buf):
            from src.memory import chat_with_memory, clear_session

            clear_session("evidence-demo")
            print("You: Hi, my name is Alice")
            r1 = chat_with_memory("Hi, my name is Alice", "evidence-demo")
            print(f"Bot: {r1}")
            print("\nYou: What's my name?")
            r2 = chat_with_memory("What's my name?", "evidence-demo")
            print(f"Bot: {r2}")
        remembered = "alice" in str(r2).lower()
        return remembered, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_07() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            from src.tools import calculator

            result = calculator("100 / 4")
            print(f'calculator("100 / 4") => {result!r}')
            print(f"expected contains: Result: 25.0")
        return "Result: 25.0" in result, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_08() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            from src.tools import get_time

            result = get_time("long")
            print(f'get_time("long") => {result!r}')
            print(f"type: {type(result).__name__}, length: {len(result)}")
        return isinstance(result, str) and len(result) > 0, buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_09() -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            from src.tools import word_counter

            result = word_counter("hello world")
            print(f'word_counter("hello world") => {result!r}')
            print('expected: "Words: 2, Characters: 11"')
        return result == "Words: 2, Characters: 11", buf.getvalue()
    except Exception:
        return False, buf.getvalue() + "\n" + traceback.format_exc()


def scenario_10() -> tuple[bool, str]:
    return run_cmd(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    )


def scenario_11() -> tuple[bool, str]:
    ok, body = run_cmd(
        [
            "gh",
            "run",
            "list",
            "--branch",
            "w13d2-challenges",
            "--limit",
            "10",
        ]
    )
    # Prefer success markers for lint + test on this branch
    lowered = body.lower()
    has_success = "success" in lowered
    has_lint = "lint" in lowered
    has_test = "test" in lowered
    return ok and has_success and has_lint and has_test, body


SCENARIOS = {
    "01": ("01-project-structure.log", "Project structure (ls src/)", scenario_01),
    "02": ("02-simple-chain.log", "Simple chain generate_and_evaluate", scenario_02),
    "03": ("03-research-chain.log", "Research chain research_pipeline", scenario_03),
    "04": ("04-memory-creation.log", "Memory creation same object", scenario_04),
    "05": ("05-memory-isolation.log", "Memory isolation alice/bob", scenario_05),
    "06": ("06-memory-chatbot.log", "Memory chatbot remembers name", scenario_06),
    "07": ("07-calculator-tool.log", 'Calculator calculator("100 / 4")', scenario_07),
    "08": ("08-time-tool.log", 'Time tool get_time("long")', scenario_08),
    "09": ("09-word-counter.log", 'Word counter word_counter("hello world")', scenario_09),
    "10": ("10-pytest.log", "Unit tests pytest tests/ -v", scenario_10),
    "11": ("11-gh-run-list.log", "GitHub Actions gh run list", scenario_11),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ids",
        nargs="*",
        help="Scenario IDs to run (default: all). Example: 01 07 10",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip Bedrock-backed scenarios (02, 03, 06)",
    )
    args = parser.parse_args()

    ids = args.ids or list(SCENARIOS.keys())
    if args.offline:
        ids = [i for i in ids if i in OFFLINE_IDS]

    sys.path.insert(0, str(ROOT))

    print(f"Evidence dir: {EVIDENCE_DIR}")
    print(f"Hub evidence: {HUB_EVIDENCE_DIR}")
    print(f"Running scenarios: {', '.join(ids)}\n")

    results = []
    for sid in ids:
        if sid not in SCENARIOS:
            print(f"[SKIP] unknown scenario id: {sid}")
            continue
        filename, title, fn = SCENARIOS[sid]
        print(f"--- {sid}: {title} ---")
        ok, body = fn()
        write_log(filename, f"## {title}\n\n{body}", ok)
        results.append((sid, ok))

    print("\n=== SUMMARY ===")
    failed = [sid for sid, ok in results if not ok]
    for sid, ok in results:
        print(f"  {sid}: {'PASS' if ok else 'FAIL'}")
    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1
    print("\nAll selected scenarios passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
