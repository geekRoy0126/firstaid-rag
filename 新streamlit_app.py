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
    background-color: #f7f9fc !important;
}

.chat-bubble {
    padding: 12px 18px;
    border-radius: 16px;
    margin: 8px 0;
    max-width: 80%;
    line-height: 1.5;
    font-size: 16px;
}

.user-bubble {
    background-color: #e3f2fd;
    color: #0d47a1;
    margin-left: auto;
    border: 1px solid #bbdefb;
}

.ai-bubble {
    background-color: #f1f8e9;
    color: #33691e;
    margin-right: auto;
    border: 1px solid #dcedc8;
}

.title {
    text-align: center;
    margin-top: 40px;
}

.doc-block {
    background: #fff;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #eee;
    margin-bottom: 8px;
    color: #000000;
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
# ================== 输入框初始化与清空逻辑 ==================

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

                # 保存 AI 回答
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.docs = docs

                st.rerun()

            except Exception as e:
                st.error(f"Error calling API: {e}")

# ------------------ RAG 文档区 ------------------
st.subheader("📚 Retrieved Documents")

docs = st.session_state.get("docs", None)
has_asked = st.session_state.get("has_asked", False)

if docs:
    # 有检索结果：正常展示
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

elif not has_asked:
    # 还没问过任何问题：显示提示
    st.caption("No documents were retrieved yet. Ask a question to see matches here.")


st.divider()
st.markdown(
    """
<span style='font-size: 0.85rem; color: #999;'>
⚠️ This assistant does not provide professional medical advice.<br>
In emergencies, call local emergency services immediately.
</span>
""",
    unsafe_allow_html=True
)
