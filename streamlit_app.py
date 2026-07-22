from datetime import date

import streamlit as st

from src.chains import summarize_project_files
from src.combo_agent import chat_with_combo, reset_combo_agent
from src.memory import (
    chat_with_memory,
    clear_session,
    get_session_history,
    session_file_path,
)
from src.special_agent import chat_with_special_agent, reset_special_agent
from src.tools import (
    calculator,
    forge_spy_codename,
    get_all_tools,
    get_time,
    search_files,
    word_counter,
)

st.set_page_config(page_title="LangChain assistant", page_icon=":material/smart_toy:")
st.title("LangChain assistant")
st.caption("Day 2 — memory chat, tools, combo agent, and Q Branch")

tab_chat, tab_tools, tab_combo, tab_special = st.tabs(
    [
        ":material/chat: Memory chat",
        ":material/build: Tools",
        ":material/smart_toy: Combo agent",
        ":material/visibility_off: Special Agent",
    ]
)

with tab_chat:
    session_id = st.text_input("Session ID", value="streamlit-demo", key="session_id")
    max_messages = st.number_input(
        "Max messages kept (last N)",
        min_value=2,
        max_value=100,
        value=20,
        step=2,
        help="Stretch goal: session history keeps only the last N messages.",
        key="max_messages",
    )
    persist_json = st.checkbox(
        "Persist session to JSON",
        value=True,
        help="Saves/loads chat history under data/sessions/<session_id>.json",
        key="persist_json",
    )
    st.caption(f"JSON path: `{session_file_path(session_id)}`")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col_clear, col_load, _ = st.columns([1, 1, 2])
    with col_clear:
        if st.button("Clear session memory", width="stretch"):
            clear_session(session_id, delete_file=True)
            st.session_state.messages = []
            st.success(f"Cleared memory for session '{session_id}'")
    with col_load:
        if st.button("Load from JSON", width="stretch"):
            history = get_session_history(
                session_id,
                max_messages=int(max_messages),
                persist=persist_json,
            )
            ui_messages = []
            for msg in history.messages:
                role = "assistant" if msg.type in ("ai", "assistant") else "user"
                if msg.type == "system":
                    continue
                ui_messages.append({"role": role, "content": msg.content})
            st.session_state.messages = ui_messages
            st.success(f"Loaded {len(ui_messages)} message(s) from JSON")

    st.markdown(
        """
**How session save / load works**

- **Persist session to JSON** saves chat turns to the file path above while you talk.
  That file survives a Streamlit restart. It does **not** survive **Clear session memory**.
- **Clear session memory** wipes the in-app chat **and deletes** the JSON file for this
  Session ID. Use it when you want a truly fresh start.
- **Load from JSON** calls `load_session_from_json` / `get_session_history` for this
  Session ID, reloads saved messages into memory, and refreshes the chat UI.

**To prove persistence:** chat with persist on → restart Streamlit (do **not** Clear) →
click **Load from JSON** → ask the bot about something you said earlier.
"""
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Message the memory chatbot")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_memory(
                    prompt,
                    session_id,
                    max_messages=int(max_messages),
                    persist=persist_json,
                )
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab_tools:
    st.subheader("Custom tools")
    st.write(
        "Invoke each tool directly (no Bedrock required). "
        "Metadata comes from the LangChain `Tool` wrappers."
    )

    tools = get_all_tools()
    tool_by_name = {tool.name: tool for tool in tools}

    with st.expander("Registered tools", expanded=False):
        for tool in tools:
            st.markdown(f"**{tool.name}** — {tool.description}")

    calc_col, time_col, word_col = st.columns(3)

    with calc_col:
        st.markdown(f"**{tool_by_name['Calculator'].name}**")
        st.caption(tool_by_name["Calculator"].description)
        with st.form("calculator_form", clear_on_submit=False):
            expression = st.text_input(
                "Expression",
                value="100 / 4",
                help="Basic math only: digits and + - * / ( )",
            )
            calc_submit = st.form_submit_button("Run calculator", width="stretch")
        if calc_submit:
            result = calculator(expression)
            st.code(result, language=None)

    with time_col:
        st.markdown(f"**{tool_by_name['CurrentTime'].name}**")
        st.caption(tool_by_name["CurrentTime"].description)
        with st.form("time_form", clear_on_submit=False):
            format_type = st.selectbox(
                "Format",
                options=["default", "short", "long", "date"],
                index=2,
            )
            time_submit = st.form_submit_button("Get time", width="stretch")
        if time_submit:
            result = get_time(format_type)
            st.code(result, language=None)

    with word_col:
        st.markdown(f"**{tool_by_name['WordCounter'].name}**")
        st.caption(tool_by_name["WordCounter"].description)
        with st.form("word_form", clear_on_submit=False):
            text = st.text_area("Text", value="hello world", height=100)
            word_submit = st.form_submit_button("Count words", width="stretch")
        if word_submit:
            result = word_counter(text)
            st.code(result, language=None)

    st.divider()
    st.markdown(f"**{tool_by_name['FileSearch'].name}**")
    st.caption(tool_by_name["FileSearch"].description)
    with st.form("file_search_form", clear_on_submit=False):
        pattern = st.text_input(
            "Pattern",
            value="*.py",
            help="Glob like *.py or substring like memory",
        )
        search_submit = st.form_submit_button("Search files", width="content")
    if search_submit:
        result = search_files(pattern)
        st.code(result, language=None)

    st.divider()
    st.markdown("**Tool → chain (stretch)**")
    st.caption(
        "Runs FileSearch first, then asks Bedrock to summarize using only that tool output."
    )
    with st.form("tool_chain_form", clear_on_submit=False):
        chain_pattern = st.text_input(
            "Pattern for tool-result chain",
            value="*.py",
            key="tool_chain_pattern",
        )
        chain_submit = st.form_submit_button(
            "Run FileSearch → summary chain",
            width="content",
        )
    if chain_submit:
        with st.spinner("Searching files, then summarizing with Bedrock..."):
            combined = summarize_project_files(chain_pattern)
        st.markdown("Tool result")
        st.code(combined["tool_result"], language=None)
        st.markdown("LLM summary (uses tool result)")
        st.write(combined["summary"])

    if "SpyCodenameGenerator" in tool_by_name:
        st.divider()
        st.markdown(f"**{tool_by_name['SpyCodenameGenerator'].name}**")
        st.caption(tool_by_name["SpyCodenameGenerator"].description)
        with st.form("codename_tools_form", clear_on_submit=False):
            cn_name = st.text_input("Name", value="Stephen McKitrick", key="tools_cn_name")
            cn_birth = st.text_input(
                "Birthdate",
                value="1985-07-21",
                help="YYYY-MM-DD preferred",
                key="tools_cn_birth",
            )
            cn_color = st.text_input("Favorite color", value="blue", key="tools_cn_color")
            cn_submit = st.form_submit_button("Forge codename", width="content")
        if cn_submit:
            st.code(
                forge_spy_codename(cn_name, cn_birth, cn_color),
                language=None,
            )

with tab_combo:
    st.subheader("Combo agent")
    st.write(
        "Stretch goal: one assistant that keeps **conversation memory** and can call "
        "**tools** (Calculator, CurrentTime, WordCounter, FileSearch, "
        "SpyCodenameGenerator) in the same thread."
    )
    st.caption(
        "Uses LangGraph `create_agent` + in-process checkpointer memory "
        "(separate from the JSON Memory chat tab)."
    )

    combo_session = st.text_input(
        "Combo session / thread ID",
        value="combo-demo",
        key="combo_session_id",
    )

    if "combo_messages" not in st.session_state:
        st.session_state.combo_messages = []

    if st.button("Clear combo chat UI", key="clear_combo_ui"):
        st.session_state.combo_messages = []
        st.success("Cleared combo chat UI (server thread memory may still exist until restart)")

    for message in st.session_state.combo_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tools_used"):
                st.caption("Tools used: " + ", ".join(message["tools_used"]))

    with st.form("combo_form", clear_on_submit=True):
        combo_prompt = st.text_area(
            "Message the combo agent",
            placeholder=(
                "Try: My favorite number is 42. "
                "Then: What is my favorite number times 2? Use the Calculator."
            ),
            height=100,
        )
        combo_submit = st.form_submit_button("Send", width="content")

    if combo_submit and combo_prompt.strip():
        st.session_state.combo_messages.append(
            {"role": "user", "content": combo_prompt.strip()}
        )
        with st.spinner("Combo agent thinking (may call tools)..."):
            result = chat_with_combo(combo_prompt.strip(), combo_session)
        st.session_state.combo_messages.append(
            {
                "role": "assistant",
                "content": result["reply"],
                "tools_used": result.get("tools_used") or [],
            }
        )
        st.rerun()

with tab_special:
    st.subheader("Special Agent — Q Branch")
    st.write(
        "Super-secret spy **codename generator**: name + birthdate + favorite color → "
        "a deterministic CLASSIFIED callsign. Same dossier always gets the same codename."
    )
    st.caption(
        "Direct forge below (no LLM). Or chat with Q — the Special Agent must call "
        "`SpyCodenameGenerator` rather than inventing names."
    )

    with st.form("special_forge_form", clear_on_submit=False):
        forge_name = st.text_input("Operative name", value="Stephen McKitrick")
        forge_birth = st.date_input(
            "Birthdate",
            value=date(1985, 7, 21),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )
        forge_color = st.selectbox(
            "Favorite color",
            options=[
                "blue",
                "red",
                "green",
                "black",
                "white",
                "gold",
                "silver",
                "purple",
                "orange",
                "yellow",
                "teal",
                "navy",
            ],
            index=0,
        )
        custom_color = st.text_input(
            "Or type a custom color (optional)",
            value="",
            placeholder="leaves selectbox if empty",
        )
        forge_submit = st.form_submit_button("Assign secret codename", width="content")

    if forge_submit:
        color = custom_color.strip() or forge_color
        dossier = forge_spy_codename(
            forge_name,
            forge_birth.isoformat(),
            color,
        )
        st.code(dossier, language=None)

    st.divider()
    st.markdown("**Brief Q (agent + tool + memory)**")

    special_session = st.text_input(
        "Special Agent thread ID",
        value="special-agent",
        key="special_session_id",
    )

    if "special_messages" not in st.session_state:
        st.session_state.special_messages = []

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear Special Agent chat UI", key="clear_special_ui"):
            st.session_state.special_messages = []
            st.success("Cleared Special Agent chat UI")
    with col_b:
        if st.button("Rebuild Special + Combo agents", key="rebuild_agents"):
            reset_special_agent()
            reset_combo_agent()
            st.success("Agents will rebuild on next message (picks up new tools)")

    for message in st.session_state.special_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tools_used"):
                st.caption("Tools used: " + ", ".join(message["tools_used"]))

    with st.form("special_chat_form", clear_on_submit=True):
        special_prompt = st.text_area(
            "Message Q",
            placeholder=(
                "Assign me a spy codename. My name is Jane Doe, "
                "born 1990-03-15, favorite color is emerald green."
            ),
            height=100,
        )
        special_submit = st.form_submit_button("Send to Q Branch", width="content")

    if special_submit and special_prompt.strip():
        st.session_state.special_messages.append(
            {"role": "user", "content": special_prompt.strip()}
        )
        with st.spinner("Q Branch processing..."):
            result = chat_with_special_agent(special_prompt.strip(), special_session)
        st.session_state.special_messages.append(
            {
                "role": "assistant",
                "content": result["reply"],
                "tools_used": result.get("tools_used") or [],
            }
        )
        st.rerun()
