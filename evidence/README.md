# Day 2 evidence logs

Captured by `scripts/run_day2_evidence.py`.

```bash
# All scenarios (Bedrock needed for 02, 03, 06)
python scripts/run_day2_evidence.py

# Offline only
python scripts/run_day2_evidence.py --offline

# One scenario
python scripts/run_day2_evidence.py 07
```

Logs are written here and mirrored to the challenges hub submission folder:

`aico-challenges-w13/.../day-2-.../submissions/Bigessfour/evidence/`

| ID  | Scenario                                | Log                                                        |
| --- | --------------------------------------- | ---------------------------------------------------------- |
| 01  | Project structure `ls src/`             | `01-project-structure.log`                                 |
| 02  | Simple chain `generate_and_evaluate`    | `02-simple-chain.log`                                      |
| 03  | Research chain `research_pipeline`      | `03-research-chain.log`                                    |
| 04  | Memory creation (same object)           | `04-memory-creation.log`                                   |
| 05  | Memory isolation alice/bob              | `05-memory-isolation.log`                                  |
| 06  | Memory chatbot remembers name           | `06-memory-chatbot.log`                                    |
| 07  | Calculator `100 / 4`                    | `07-calculator-tool.log`                                   |
| 08  | Time tool `long`                        | `08-time-tool.log`                                         |
| 09  | Word counter                            | `09-word-counter.log`                                      |
| 10  | `pytest tests/ -v`                      | `10-pytest.log`                                            |
| 11  | `gh run list` (lint + test)             | `11-gh-run-list.log`                                       |
| 12  | Streamlit memory chat (Steve / 59)      | `screenshots/12-streamlit-memory-chat.png`                 |
| 13  | Streamlit tools tab (calc/time/words)   | `screenshots/13-streamlit-tools-tab.png`                   |
| 14  | Streamlit calculator `100 / 4` → 25.0   | `screenshots/14-streamlit-calculator-result.png`           |
| 15  | Streamlit time tool `long` result       | `screenshots/15-streamlit-time-result.png`                 |
| 16  | Streamlit word counter result           | `screenshots/16-streamlit-word-counter-result.png`         |
| 17  | Streamlit max messages (last N) control | `screenshots/17-streamlit-max-messages-control.png`        |
| 18  | Streamlit FileSearch tool demo (PDF)    | `screenshots/18-streamlit-file-search.pdf`                 |
| 19  | Streamlit tool→chain FileSearch summary | `screenshots/19-streamlit-tool-result-chain.pdf`           |
| 20  | JSON session persistence sample         | `20-session-persistence-streamlit-demo.json`               |
| 21  | Streamlit JSON persist UI               | `screenshots/21-streamlit-json-persistence-ui.png`         |
| 22  | Streamlit JSON save/load instructions   | `screenshots/22-streamlit-json-save-load-instructions.png` |
| 23  | Special Agent / Q Branch spy codename   | `screenshots/23-streamlit-special-agent-spy-codename.pdf`  |
| 24  | Special Agent chat → SpyCodenameGenerator | `screenshots/24-streamlit-special-agent-chat-codename.png` |

**23 — heroic Q Branch dossier:** Streamlit **Special Agent** tab forging a CLASSIFIED callsign from name + birthdate + favorite color (`COBALT COBRA-21` / `SM-85`). Our contribution to the ongoing struggle against the bad guys.

**24 — chat path:** Brief Q (agent + tool + memory) assigned `VIOLET SHARK-23` / callsign `SM-66` via **Tools used: SpyCodenameGenerator** (not invented by the LLM).
