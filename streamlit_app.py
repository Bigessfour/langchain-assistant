import streamlit as st
from src.chains import chat

st.title("🤖 Multilingual Chatbot")

language = st.selectbox(
    "Choose Language:",
    ["English", "Spanish", "French", "German", "Japanese"],
)

user_input = st.text_area("Your message:")

if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            response = chat(language, user_input)
        st.write("🤖 Response:", response)
    else:
        st.warning("Please enter a message")
