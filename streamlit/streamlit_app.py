import streamlit as st
import requests
import json

API_URL = "https://stored-yale-expectations-bangkok.trycloudflare.com/ask"

st.set_page_config(page_title="First Aid RAG Assistant", page_icon="✚", layout="centered")

# ------------------ Custom CSS with Avatars ------------------
chat_css = """
<style>
body {
    background-color: #f5f8fc;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1a1d26;
    margin: 0;
    padding: 0;
}

/* ===== AVATARS ===== */
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    border: 2px solid #e63946;
    box-shadow: 0 2px 5px rgba(230,57,70,0.12);
}

/* Wrapper for bubbles + avatars */
.bubble-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    width: 100%;
}

/* Positioning wrappers */
.user-wrapper {
    justify-content: flex-end;
}
.ai-wrapper {
    justify-content: flex-start;
}

/* ===== CHAT BUBBLES ===== */
.chat-bubble {
    padding: 14px 20px;
    border-radius: 22px;
    margin: 10px 0;
    max-width: 65%;
    line-height: 1.6;
    font-size: 15.2px;
    box-shadow: 0 2px 7px rgba(0, 0, 0, 0.045);
    transition: transform 0.15s ease, box-shadow 0.22s ease;
}

.chat-bubble:hover {
    transform: translateY(-1.5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.09);
}

/* User bubble */
.user-bubble {
    background-color: #d9e7fd;
    color: #032b7a;
    border: 1px solid #aac9f8;
    font-weight: 500;
}

/* AI bubble */
.ai-bubble {
    background-color: #ffffff;
    color: #1f2533;
    border-left: 4px solid #e63946;
    font-weight: 500;
}

/* Document block */
.doc-block {
    background: #fff;
    padding: 15px;
    border-radius: 13px;
    border: 1px solid #f2dede;
    border-left: 5px solid #e63946;
    margin-bottom: 13px;
    color: #2a2f3c;
    font-size: 14.6px;
    box-shadow: 0 1px 5px rgba(230,57,70,0.05);
}

.doc-block::before {
    content: "🧰 Medical Source Extract";
    display: block;
    font-weight: 700;
    font-size: 13.2px;
    color: #b71c1c;
    margin-bottom: 7px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 7px;
}
::-webkit-scrollbar-thumb {
    background: #e63946;
    border-radius: 4px;
}
::-webkit-scrollbar-track {
    background: #eef2f8;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ------------------ Page Title ------------------
st.markdown("<div class='title'>First Aid RAG Assistant</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Ask any first-aid related question. Your RAG system will retrieve knowledge and respond.</p>", unsafe_allow_html=True)

# ------------------ Chat History ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 头像占位（你之后可以换成本地 assets 目录）
USER_AVATAR = "https://i.pravatar.cc/150?img=12"
BOT_AVATAR = "https://i.pravatar.cc/150?img=5"

def render_message(role, text):
    if role == "user":
        st.markdown(
            f"""
            <div class="bubble-wrapper user-wrapper">
                <img class="avatar" src="{USER_AVATAR}">
                <div class="chat-bubble user-bubble">{text}</div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="bubble-wrapper ai-wrapper">
                <img class="avatar" src="{BOT_AVATAR}">
                <div class="chat-bubble ai-bubble">{text}</div>
            </div>
            """, unsafe_allow_html=True)

# Render existing chat bubbles
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# ------------------ Input Box (Ctrl+Enter Works via Form) ------------------
if "question_box" not in st.session_state:
    st.session_state.question_box = ""
if "clear_question" not in st.session_state:
    st.session_state.clear_question = False

if st.session_state.clear_question:
    st.session_state.question_box = ""
    st.session_state.clear_question = False

with st.form("qa_form"):
    question = st.text_area("Your question:", height=80, key="question_box")
    submitted = st.form_submit_button("Ask")

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        st.session_state.clear_question = True
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("✚ Retrieving first-aid knowledge..."):
            try:
                res = requests.post(API_URL, json={"question": question.strip()})
                data = res.json()
                answer = data.get("answer", "")
                docs = data.get("retrieved_docs", [])
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.docs = docs
                st.rerun()
            except Exception as e:
                st.error(f"Error calling API: {e}")

# ------------------ Retrieved Documents Section ------------------
messages = st.session_state.get("messages", [])
has_asked = any(m.get("role") == "user" for m in messages)
docs = st.session_state.get("docs", None)

if has_asked:
    st.subheader("📚 Retrieved Documents")
    if docs:
        for i, d in enumerate(docs, start=1):
            with st.expander(f"Document {i} • score={d.get('score', 0):.4f}"):
                st.markdown(
                    f"""
                    <div class='doc-block'>
                    <strong>Q:</strong> {d.get('q','')}<br><br>
                    <strong>A:</strong> {d.get('a','')}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.caption("No documents were retrieved for this question.")

# ------------------ Footer Disclaimer ------------------
st.divider()
st.markdown(
    """
<div style='text-align: center; margin-top: 36px;'>
    <span style='font-size: 0.88rem; color: #888888;'>
        ⚠️ This assistant does not provide professional medical advice.<br>
        In emergencies, please call local emergency services immediately.
    </span>
</div>
""",
    unsafe_allow_html=True
)
