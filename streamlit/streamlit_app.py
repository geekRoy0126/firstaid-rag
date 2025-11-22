import streamlit as st
import requests
import json
import time

# ------------------ BACKEND URL (已替换) ------------------
API_URL = "https://map-disclosure-honey-howard.trycloudflare.com/ask"

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="First Aid Assistant",
    page_icon="🚑",
    layout="centered",
)

# ------------------ DARK THEME CSS ------------------
dark_css = """
<style>
    body {
        background-color: #000000 !important;
    }
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #333333;
    }
    .bubble {
        padding: 12px 18px;
        border-radius: 16px;
        margin: 8px 0;
        max-width: 80%;
        line-height: 1.5;
        font-size: 16px;
        display: inline-block;
    }
    .user-bubble {
        background-color: #2b2b2b;
        color: #d9d9d9;
        margin-left: auto;
        border: 1px solid #3a3a3a;
    }
    .ai-bubble {
        background-color: #1a1a1a;
        border-left: 4px solid #ff4d4f;
        border: 1px solid #2a2a2a;
        color: #e6e6e6;
    }
    .stButton>button {
        background-color: #ff4d4f;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #ff6666;
        transition: 0.2s;
    }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown(
    "<h1 style='text-align:center; color:#ff4d4f;'>🚑 First Aid Assistant</h1>",
    unsafe_allow_html=True
)

# ------------------ CHAT HISTORY ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    role = msg["role"]
    bubble_class = "user-bubble" if role == "user" else "ai-bubble"
    st.markdown(
        f"<div class='bubble {bubble_class}'>{msg['content']}</div>",
        unsafe_allow_html=True
    )

# ------------------ INPUT ------------------
user_input = st.text_area("Describe your symptoms or ask a first-aid question:", height=80)

if st.button("Send"):
    if user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(
            f"<div class='bubble user-bubble'>{user_input}</div>",
            unsafe_allow_html=True
        )

        # Call backend
        with st.spinner("Analyzing symptoms..."):
            try:
                res = requests.post(API_URL, json={"question": user_input})
                data = res.json()
                answer = data.get("answer", "No answer returned.")
            except Exception as e:
                answer = f"⚠️ Cannot reach server.\n\n{e}"

        # Add AI message
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.markdown(
            f"<div class='bubble ai-bubble'>{answer}</div>",
            unsafe_allow_html=True
        )


