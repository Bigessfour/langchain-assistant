# Week13-Day2 Challenge completion steps

**Primary narrative for the Day 2 PR** (also posted under Conversations). First-person notes while extending Day 1 `langchain-assistant` with chains, memory, and tools.

### TAs — pick your own spy codename
Streamlit → **Special Agent** tab (or Tools → SpyCodenameGenerator). Enter your name, birthdate, and favorite color. Same inputs always forge the same CLASSIFIED callsign. Evidence: `evidence/screenshots/23-streamlit-special-agent-spy-codename.pdf`.

Brief: `aico-challenges-w13/day-2-composability-chains-memory-and-tools/challenge-1-extend-your-ai-application-with-chains-memory-and-tools.md`

App repo: `/Users/stephenmckitrick/AICO-ECHO/langchain-assistant` on branch `w13d2-challenges`
Hub repo: `/Users/stephenmckitrick/AICO-ECHO/aico-challenges-w13/aico-challenges-w13` on branch `w13-challenges`
App PR: https://github.com/Bigessfour/langchain-assistant/pull/1
Hub PR: https://github.com/codeplatoon-devops/aico-challenges-w13/pull/1

---

## What I did

### Setup
I pulled Day 1 forward instead of starting over. Scaffolded my Day 2 submission folder under the challenges hub, made branch `w13d2-challenges` on the app, and confirmed `git` / `gh` / python / AWS (`codeplatoon`) were good.

`langchain-core` was already in `requirements.txt` from yesterday. I also had to add `langchain-classic` because LangChain 1.x moved the old `LLMChain` / sequential chain stuff out of the main package — the brief sample imports broke until I fixed that.

### Core challenge pieces
I pasted in / adapted the brief code for:

- `src/chains.py` — simple sequential chain + research pipeline
- `src/memory.py` — session memory + `chat_with_memory`
- `src/tools.py` — calculator, time, word counter

Kept Day 1 `client.py` and `prompts.py`. Added matching tests (`test_chains`, `test_memory`, `test_tools`). Updated `main.py` so I can demo tools → chains → memory from the CLI. Pointed Streamlit and the lab wrapper at the memory chat instead of the old Day 1 `chat()`.

Pytest is green (no AWS for unit tests). Lint + test workflows went green on the PR after I pushed. Live Bedrock demos for chains/memory also worked with my `codeplatoon` profile.

### Evidence
I built `scripts/run_day2_evidence.py` so each testing scenario writes its own log. Logs land in `langchain-assistant/evidence/` and get copied into the hub submission evidence folder. Also grabbed Streamlit screenshots for memory chat and each tool run.

```bash
python scripts/run_day2_evidence.py
python scripts/run_day2_evidence.py --offline
```

App PR is open: https://github.com/Bigessfour/langchain-assistant/pull/1

---

## Stretch: memory size limiting (last N messages)

I wanted session memory to stop growing forever, so I added a limit that only keeps the last N messages.

### How I did it
1. Made a `LimitedChatMessageHistory` class that subclasses `InMemoryChatMessageHistory`.
2. Override `add_message` — after a message is appended, call `trim()`.
3. `trim()` slices the list to `messages[-max_messages:]` when we’re over the limit.
4. Default N is 20 (`DEFAULT_MAX_MESSAGES`). New sessions get a limited history automatically.
5. `get_session_history(session_id, max_messages=...)` can set/change the limit; if I lower N on an existing session it trims right away.
6. `chat_with_memory(..., max_messages=N)` passes that through before the bot runs.
7. In Streamlit I added a **Max messages kept (last N)** number input and pass it into `chat_with_memory`.

Unit tests cover: history is the limited type, adding past N drops the oldest, and lowering N trims immediately.

### Evidence for this stretch
Screenshot of the Streamlit control:

- `evidence/screenshots/17-streamlit-max-messages-control.png`
- hub copy under `submissions/Bigessfour/evidence/screenshots/` same filename

Shows Session ID `streamlit-demo` and Max messages kept set to `20`.

---

## Stretch: file search tool

I added a fourth tool that searches files under the current working directory.

### How I did it
1. Wrote `search_files(pattern)` in `src/tools.py` using `Path.cwd().rglob("*")`.
2. Pattern can be a glob (`*.py`) or a substring (`memory`).
3. Skips junk folders like `venv`, `.git`, `__pycache__`, `.pytest_cache`.
4. Caps the printed list at 50 matches so the output doesn’t explode.
5. Wrapped it as a LangChain `Tool` named `FileSearch` and included it in `get_all_tools()`.
6. Added Streamlit form under Tools (pattern input + Search files).
7. Tests use a temp directory so they don’t depend on my real repo layout.

Try in Streamlit Tools tab with `*.py` or `memory`.

### Evidence for this stretch
I ran FileSearch from the Streamlit Tools tab (pattern like `*.py`) and exported the page as a PDF for proof:

- `evidence/screenshots/18-streamlit-file-search.pdf`
- hub copy: `submissions/Bigessfour/evidence/screenshots/18-streamlit-file-search.pdf`

(Original export from my Desktop: `LangChain assistant.pdf`.)

### Troubleshooting: Streamlit ImportError after adding FileSearch

After I wired `search_files` into `streamlit_app.py`, Streamlit blew up with:

```text
ImportError: cannot import name 'search_files' from 'src.tools'
(.../langchain-assistant/src/tools.py)
```

The function was already in `src/tools.py` and imported fine from a normal Python shell — Streamlit was just stuck on an old in-memory import / stale `__pycache__` from before I added the tool.

What fixed it:
1. Stopped the old Streamlit process on port 8501
2. Deleted `src/__pycache__`
3. Confirmed `from src.tools import search_files` works and `get_all_tools()` lists `FileSearch`
4. Restarted with `streamlit run streamlit_app.py` and hard-refreshed the browser

---

---

## Stretch: chain that uses tool results in its output

This one means: run a real tool first, then feed that output into an LLM chain so the final answer is grounded in the tool — not made up.

### How I did it
1. Added `collect_file_search_context(pattern)` — just calls `search_files` (no AWS).
2. Added `build_tool_result_chain(llm)` — prompt takes `{pattern}` and `{tool_result}` and asks for a short project layout summary using only those paths.
3. Added `summarize_project_files(pattern)` — runs the tool, then the chain, returns:
   - `tool_result` (from FileSearch)
   - `summary` (from Bedrock)
4. Hooked it into `main.py` and Streamlit Tools tab as **FileSearch → summary chain**.
5. Unit tests cover the tool step without AWS; the full LLM path needs Bedrock.

### Evidence for this stretch
I ran **FileSearch → summary chain** in Streamlit with pattern `*.py` and saved the page as a PDF. It shows:
- Tool result: 15 `.py` files listed from the real search
- LLM summary that talks about those same paths (`main.py`, `src/chains.py`, tests, etc.)

Renamed from `LangChain assistant.pdf` to:

- `evidence/screenshots/19-streamlit-tool-result-chain.pdf`
- hub copy under `submissions/Bigessfour/evidence/screenshots/` same name

---

---

## Stretch: session persistence via JSON

I wanted chat memory to survive a Streamlit/app restart, so I save each session to a JSON file.

### How I did it
1. Sessions write to `data/sessions/<safe_session_id>.json` (folder is gitignored).
2. JSON shape: `session_id`, `max_messages`, and a `messages` list of `{type, content}`.
3. `save_session_to_json` / `load_session_from_json` handle read/write.
4. `get_session_history` loads from disk the first time it sees a session id.
5. `LimitedChatMessageHistory.add_message` saves after each new message when `persist=True`.
6. `chat_with_memory(..., persist=True)` turns it on; `clear_session` deletes the JSON file too.
7. Streamlit: checkbox **Persist session to JSON**, shows the file path, and a **Load from JSON** button to refresh the chat UI from disk.

### How to prove it
1. Chat with persist on (session id `streamlit-demo`).
2. Restart Streamlit / refresh.
3. Click **Load from JSON** — old turns should come back.
4. Or open `data/sessions/streamlit-demo.json` and check the messages.

### Evidence for this stretch
I turned on **Persist session to JSON**, chatted under session `streamlit-demo`, and captured:

1. The saved session file (copy of `data/sessions/streamlit-demo.json`):
   - `evidence/20-session-persistence-streamlit-demo.json`
   - Shows `session_id`, `max_messages: 20`, and human/ai messages
2. Screenshot of the Memory chat UI with persist checked and the JSON path shown:
   - `evidence/screenshots/21-streamlit-json-persistence-ui.png`
3. Screenshot after I added the save/load instructions under the buttons:
   - `evidence/screenshots/22-streamlit-json-save-load-instructions.png`

Same files mirrored under the hub submission `evidence/` folder.

### Troubleshooting: Streamlit ImportError after adding JSON persistence

After wiring `session_file_path` into `streamlit_app.py`, Streamlit hit the same stale-import issue as FileSearch:

```text
ImportError: cannot import name 'session_file_path' from 'src.memory'
```

The function was already in `src/memory.py` and imported fine from a normal Python shell. Fix was the same as before: kill the Streamlit process on 8501, delete `src/__pycache__`, restart `streamlit run streamlit_app.py`, hard-refresh the browser.

### Troubleshooting: Clear wiped my JSON (and I thought persistence failed)

I told the bot something specific (“today, July 21st, 2026 is the first day of the rest of my life”) and it got saved into `data/sessions/streamlit-demo.json`. Then I hit **Clear session memory** and asked again — it didn’t have that date anymore.

What was going on:
1. **Clear session memory** is a full wipe — in-app chat **and** the JSON file for that Session ID.
2. Persistence means the file survives a **Streamlit restart**, not Clear.
3. After Clear, a new chat with persist on just creates a fresh JSON, so the old fact is gone.

What I changed so the next person (or me) doesn’t get confused:
- Added a **How session save / load works** blurb under the Clear / Load buttons in Streamlit.
- Explains Persist vs Clear vs **Load from JSON** (`load_session_from_json` / `get_session_history`).
- Includes the prove-it path: chat with persist on → restart (don’t Clear) → **Load from JSON** → ask about something said earlier.

Evidence of that UI text: `evidence/screenshots/22-streamlit-json-save-load-instructions.png`

### Troubleshooting: thought JSON failed after reload — it was Nova Lite privacy refusal

I reloaded the Streamlit UI (did **not** Clear), asked what date I had called “the first day of the rest of my life,” and got a canned privacy answer:

> Sorry, but I can't provide specific details about what you mentioned in previous chats due to privacy and confidentiality policies...

I figured either Bedrock was blocking me, or memory didn’t actually come back from JSON.

What we found when we dug in:
1. `data/sessions/streamlit-demo.json` still had my July 21st, 2026 line in it.
2. After emptying the in-memory store (simulating a restart), `load_session_from_json` / `get_session_history` pulled all those messages back — persistence worked.
3. Asking Bedrock again **with that history already loaded** still returned the same privacy refusal.
4. Even a tighter ask (“quote the exact date from our conversation history”) got refused.
5. So this was **not** a session disconnect. Nova Lite treated recalling that date / “previous chat” personal detail as something it shouldn’t answer.

Also: **Load from JSON** mainly refreshes the on-screen chat. The backend still rehydrates from the JSON file on the next send even if the UI looks empty after a browser reload.

If I needed to avoid the Nova Lite privacy guards for demos, I’d try (in order):
1. **Better demo facts** — use a neutral codeword (`Remember my project codeword is BLUE-ORBIT`) instead of dates / “personal life” phrasing.
2. **System prompt tweak** in `build_memory_chatbot` — tell the model it *should* recall facts the user explicitly shared earlier in this same session / history placeholder.
3. **Ask differently** — “From the history messages, what exact string did I type about July?” rather than “what personal date did I mention in previous chats?”
4. **Stronger fix if still blocked** — switch models, or add a tiny non-LLM recall helper that reads the JSON/history and answers fact lookups without sending that question through Nova’s refusal path.
5. I did **not** implement those fixes for this challenge; documenting the discovery is enough for now.

---

---

## Stretch: combined assistant (memory + tools) — Combo agent tab

I wanted one place that can remember what I said **and** call tools in the same conversation.

### How I did it
1. Added `src/combo_agent.py` using LangChain 1.x `create_agent` with my existing tools from `get_all_tools()`.
2. Wired a LangGraph `MemorySaver` checkpointer so each **thread_id** (combo session ID) keeps conversation memory in-process.
3. `chat_with_combo(message, session_id)` invokes the agent and returns `{reply, tools_used}`.
4. Nova sometimes returns content as block lists, so I normalize that with `_extract_text`.
5. Streamlit: third tab **Combo agent** (form input — Streamlit only allows one `chat_input` per app, and Memory chat already uses it).
6. This memory is separate from the JSON Memory chat tab on purpose (agent checkpointer vs our JSON session files).

Try: “My favorite number is 42” then “What is my favorite number times 2? Use the Calculator.”

---

## Stretch: Special Agent — spy codename generator

Wanted a Bond / Q Branch flourish: assign a secret codename from **name + birthdate + favorite color**.

### How I did it
1. Added `forge_spy_codename()` in `src/tools.py` — deterministic mapping (month → animal, color → codeword, day/year → tags). Same inputs always same codename.
2. Wrapped it as `SpyCodenameGenerator` (`StructuredTool` with name / birthdate / favorite_color).
3. Included it in `get_all_tools()` (fifth tool) so Combo agent can call it too.
4. Added `src/special_agent.py` — Q persona that **must** call the tool instead of inventing names.
5. Streamlit fourth tab **Special Agent**: direct forge form + chat with Q.
6. Also exposed a forge form on the Tools tab for quick demos without Bedrock.

Try: name `Stephen McKitrick`, birthdate `1985-07-21`, color `blue` → expect something like `COBALT COBRA-21` / callsign `SM-85`.

### Evidence
- Heroic Q Branch dossier PDF: `evidence/screenshots/23-streamlit-special-agent-spy-codename.pdf`
  (mirrored under the challenges hub `submissions/Bigessfour/evidence/screenshots/`)
- Shows Special Agent forge → `COBALT COBRA-21` / `SM-85` for the McKitrick dossier.
- Filed under: helping the country against the bad guys.
- Chat path (agent + tool): `evidence/screenshots/24-streamlit-special-agent-chat-codename.png`
  - Asked Q to assign a codename (name / birthdate `10/23/1966` / purple).
  - Reply: `VIOLET SHARK-23`, callsign `SM-66`, caption **Tools used: SpyCodenameGenerator**.

---

## Submission status
- [x] Commit/push stretch + evidence onto app PR (`w13d2-challenges`)
- [x] Commit/push Day 2 hub submission onto `w13-challenges`
- [x] This completion-steps doc is the front of the PR conversation for TAs
