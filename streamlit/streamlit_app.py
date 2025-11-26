import streamlit as st
import requests
import json
import time

API_URL = "http://host.docker.internal:8000/ask"

st.set_page_config(page_title="First Aid RAG Assistant", page_icon="🚑", layout="centered")

# ------------------ Custom CSS ------------------
chat_css = """
<style>
body {
    background-color: #f5f8fc;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1a1d26;
    margin: 0;
    padding: 0;
}

/* ===== CHAT BUBBLES ===== */
.chat-bubble {
    padding: 14px 20px;
    border-radius: 22px;
    margin: 12px 0;
    max-width: 70%;
    line-height: 1.65;
    font-size: 15.3px;
    box-shadow: 0 2px 7px rgba(0, 0, 0, 0.045);
    transition: transform 0.15s ease, box-shadow 0.22s ease;
}

.chat-bubble:hover {
    transform: translateY(-1.6px);
    box-shadow: 0 4px 13px rgba(0, 0, 0, 0.09);
}

/* User messages */
.user-bubble {
    background-color: #d9e7fd;
    color: #032b7a;
    margin-left: auto;
    border: 1px solid #aac9f8;
    font-weight: 500;
}

/* AI messages */
.ai-bubble {
    background-color: #ffffff;
    color: #1f2533;
    margin-right: auto;
    border-left: 4px solid #e63946;
    font-weight: 500;
    font-size: 15.1px;
}

/* ===== RED CROSS TITLE ===== */
.title {
    text-align: center;
    margin-top: 26px;
    margin-bottom: 20px;
    font-size: 28px;
    font-weight: 800;
    color: #c62a2a;
    letter-spacing: -0.4px;
}

.title::after {
    content: "✚";
    display: block;
    font-size: 36px;
    color: #e63946;
    margin-top: 6px;
    animation: cross-pulse 1.6s infinite alternate ease-in-out;
}

@keyframes cross-pulse {
    0% { opacity: 0.55; transform: scale(0.92); }
    100% { opacity: 1; transform: scale(1.18); }
}

/* ===== DOCUMENT BLOCK (RAG retrieved sources) ===== */
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

/* ===== LOADING ELEMENT (for LLM thinking) ===== */
.loading-cross {
    text-align: center;
    font-size: 26px;
    font-weight: 700;
    color: #e63946;
    animation: cross-loader 1.1s infinite alternate ease-in-out;
}

@keyframes cross-loader {
    0% { opacity: 0.4; transform: scale(0.9) rotate(-6deg); }
    100% { opacity: 1; transform: scale(1.22) rotate(6deg); }
}

/* ===== EMERGENCY ALERT BLOCK ===== */
.emergency-block {
    background: #ffecec;
    border-left: 6px solid #d32f2f;
    padding: 12px 17px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 15px;
    color: #8b0000;
    margin: 14px auto;
    width: 82%;
    box-shadow: 0 2px 9px rgba(211, 47, 47, 0.11);
    animation: alert-flash 1.8s infinite alternate ease-in-out;
}

@keyframes alert-flash {
    0% { box-shadow: 0 0 6px rgba(255,80,80,0.25); }
    100% { box-shadow: 0 0 15px rgba(255,40,40,0.38); }
}

/* ===== KEY MEDICAL ACTION HIGHLIGHT ===== */
.action-highlight {
    background: #e63946;
    padding: 6px 12px;
    border-radius: 8px;
    display: inline-block;
    color: white;
    font-weight: 700;
    font-size: 14.8px;
}

/* ===== SCROLLBAR (minimal + medical tone) ===== */
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

# ------------------ 页面标题 ------------------
st.markdown("<h1 class='title'>🚑 First Aid RAG Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Ask any first-aid related question. Your local RAG system will retrieve documents and respond.</p>", unsafe_allow_html=True)

# ------------------ 聊天历史 ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息气泡
for msg in st.session_state.messages:
    bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# ------------------ 输入栏 ------------------
# 初始化 question_box（输入框的 state）
if "question_box" not in st.session_state:
    st.session_state.question_box = ""

# 初始化 clear_question（是否在下次 rerun 清空输入框）
if "clear_question" not in st.session_state:
    st.session_state.clear_question = False

# 如果上一轮设置了需要清空 → 在渲染控件之前清空输入框
if st.session_state.clear_question:
    st.session_state.question_box = ""      # 清空输入框内容
    st.session_state.clear_question = False # 重置开关

#( so Ctrl+Enter works)
with st.form("qa_form"):
    question = st.text_area(
        "Your question:",
        height=80,
        key="question_box"
    )
    submitted = st.form_submit_button("Ask")   # Ctrl+Enter 会触发这里

# ---- When user submits ----
if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # 下一轮 rerun 前清空输入框
        st.session_state.clear_question = True

        # 用户消息
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            try:
                res = requests.post(API_URL, json={"question": question})
                data = res.json()

                answer = data.get("answer", "")
                docs = data.get("retrieved_docs", [])

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.docs = docs

                st.rerun()

            except Exception as e:
                st.error(f"Error calling API: {e}")

# ------------------ RAG 文档区 ------------------

messages = st.session_state.get("messages", [])
# 只要有一条 user 消息，就说明已经问过问题
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
                    <strong>Q:</strong> {d.get('q', '')}<br><br>
                    <strong>A:</strong> {d.get('a', '')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No documents were retrieved for this question.")

st.divider()
st.markdown(
    """
<div style='text-align: center; margin-top: 40px;'>
    <span style='font-size: 0.9rem; color: #bbbbbb;'>
        ⚠️ This assistant does not provide professional medical advice.<br>
        In emergencies, please call local emergency services immediately.
    </span>
</div>
""",
    unsafe_allow_html=True
)
