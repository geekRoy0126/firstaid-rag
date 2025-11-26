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
    background-color: #f2f6fb !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Container improvements */
#chat-container {
    scroll-behavior: smooth;
}

/* Bubbles general */
.chat-bubble {
    padding: 14px 20px;
    border-radius: 20px;
    margin: 10px 0;
    max-width: 75%;
    line-height: 1.6;
    font-size: 15.5px;
    transition: transform 0.15s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.chat-bubble:hover {
    transform: translateY(-1.5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* User bubble */
.user-bubble {
    background-color: #dceafc;
    color: #084298;
    margin-left: auto;
    border: 1px solid #b6d4fe;
}

/* AI bubble */
.ai-bubble {
    background-color: #e6f4ea;
    color: #146c43;
    margin-right: auto;
    border: 1px solid #a3cfbb;
}

/* Title improvements */
.title {
    text-align: center;
    margin-top: 32px;
    font-size: 24px;
    font-weight: 700;
    color: #c62a2a;
    letter-spacing: -0.5px;
}

/* Medical red pulse for first-aid visual vibe */
.title::after {
    content: '';
    display: block;
    width: 60px;
    height: 4px;
    background: #ff4d4d;
    margin: 8px auto 0;
    border-radius: 3px;
    animation: pulse 1.8s infinite ease-in-out;
}

@keyframes pulse {
    0% { opacity: 0.5; transform: scaleX(0.9); }
    50% { opacity: 1; transform: scaleX(1.1); }
    100% { opacity: 0.5; transform: scaleX(0.9); }
}

/* Doc/reference block */
.doc-block {
    background: #ffffff;
    padding: 14px;
    border-radius: 14px;
    border-left: 4px solid #ff6b6b;
    margin-bottom: 10px;
    color: #1a1a1a;
    font-size: 14.4px;
    box-shadow: 0 1.5px 5px rgba(0, 0, 0, 0.05);
}

/* Optional: alert-like block for first aid extracted docs */
.doc-block::before {
    content: '🩺 Reference';
    display: block;
    font-weight: 600;
    font-size: 13px;
    color: #d32f2f;
    margin-bottom: 6px;
}

/* Rounded code blocks inside bubbles */
.chat-bubble code {
    background: rgba(0,0,0,0.04);
    padding: 3px 6px;
    border-radius: 6px;
    font-size: 14px;
    font-family: 'SF Mono', Consolas, 'Courier New', monospace;
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
