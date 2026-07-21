import streamlit as st

from src.memory import chat_with_memory, clear_session

st.title("Memory Chatbot")

session_id = st.text_input("Session ID:", value="streamlit-demo")

if st.button("Clear session memory"):
    clear_session(session_id)
    st.success(f"Cleared memory for session '{session_id}'")

user_input = st.text_area("Your message:")

if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            response = chat_with_memory(user_input, session_id)
        st.write("Response:", response)
    else:
        st.warning("Please enter a message")
