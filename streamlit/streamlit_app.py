import streamlit as st
import requests
import json

API_URL = "https://pac-games-differ-darwin.trycloudflare.com/ask"

st.set_page_config(page_title="First Aid Assistant", page_icon="🚑", layout="wide")

# ------------------ STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str}]
if "docs" not in st.session_state:
    st.session_state.docs = []

# ------------------ CSS ------------------
chat_css = """
<style>
body {
    background-color: #f7f9fc !important;
}

/* 聊天容器 */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* 通用气泡样式 */
.chat-bubble {
    padding: 12px 16px;
    border-radius: 14px;
    max-width: 80%;
    line-height: 1.5;
    font-size: 16px;
}

/* 用户气泡（右侧） */
.user-bubble {
    margin-left: auto;
    background: #e3f2fd;
    color: #0d47a1;
    border: 1px solid #bbdefb;
}

/* 机器人气泡（左侧） */
.bot-bubble {
    margin-right: auto;
    background: #f5f5f5;
    border-left: 4px solid #d32f2f;
    color: #212121;
}

/* 顶部标题居中 */
.main-title {
    text-align: center;
    color: #d32f2f;
    margin-bottom: 1rem;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("<h1 class='main-title'>🚑 First Aid Assistant</h1>", unsafe_allow_html=True)

# ------------------ LAYOUT ------------------
chat_col, docs_col = st.columns([2, 1])

with chat_col:
    st.markdown("### 💬 Chat")

    # 显示历史对话
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            bubble_class = "user-bubble"
        else:
            bubble_class = "bot-bubble"

        st.markdown(
            f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 输入栏
    user_input = st.text_input(
        "Describe symptoms or ask a first-aid question...",
        key="user_input",
        placeholder="e.g., I cut my finger and it's bleeding a bit. What should I do?",
    )

    send = st.button("Send", type="primary")

    if send and user_input.strip():
        question = user_input.strip()

        # 1. 先把用户消息放进历史
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        # 2. 调用后端接口
        try:
            with st.spinner("Assistant is thinking..."):
                res = requests.post(API_URL, json={"question": question}, timeout=60)
                res.raise_for_status()
                data = res.json()
        except Exception as e:
            answer = f"❌ 后端出错：{e}"
            docs = []
        else:
            answer = data.get("answer", "⚠️ 后端没有返回 answer 字段")
            docs = data.get("retrieved_docs", [])

        # 3. 保存机器人回复 & 文档
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.docs = docs

        # 清空输入框
        st.session_state.user_input = ""

        # 触发页面刷新以立即显示新内容
        st.rerun()

with docs_col:
    st.subheader("📚 Retrieved Documents")

    docs = st.session_state.docs or []
    if not docs:
        st.info("当前还没有检索到文档。提一个问题试试？")
    else:
        for i, d in enumerate(docs, start=1):
            score = d.get("score", 0.0)
            q = d.get("q", "")
            a = d.get("a", "")
            with st.expander(f"Document {i} (score={score:.4f})"):
                st.markdown(
                    f"""
                    <div style='background:#ffffff;
                                padding:12px;
                                border-radius:10px;
                                border:1px solid #eee;'>
                        <strong>Q:</strong> {q}<br><br>
                        <strong>A:</strong> {a}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
