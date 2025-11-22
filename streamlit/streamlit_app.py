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

# ------------------ CSS（WhatsApp 风格） ------------------
chat_css = """
<style>
body {
    background-color: #e5ddd5 !important;
}

/* 聊天容器（调小高度 + 自动滚动） */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 12px 16px;
    height: 450px;              /* 原来 600 太大了，改成更合适 */
    overflow-y: auto;
    background: #fafafa;
    border-radius: 12px;
    border: 1px solid #ddd;
}

/* 通用气泡 - 限制宽度，不让铺满一整行 */
.chat-bubble {
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 60%;             /* ⭐ 改成 60%，自然居左/居右，看起来像聊天 */
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 1px rgba(0,0,0,0.12);
}

/* 用户（右侧，绿色泡泡） */
.user-bubble {
    background: #dcf8c6;
    margin-left: auto;
}

/* AI（左侧，白色泡泡） */
.bot-bubble {
    background: #ffffff;
    margin-right: auto;
}

/* 顶部标题美化 */
.main-title {
    text-align: center;
    color: #075E54;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 1rem;
    font-size: 32px;
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

    # 聊天容器
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"

        st.markdown(
            f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

    # 关闭聊天容器
    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ 自动滚动到底部 ------------------
    scroll_js = """
    <script>
        const containers = window.parent.document.getElementsByClassName('chat-container');
        if (containers.length > 0) {
            const chat = containers[0];
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
    """
    st.markdown(scroll_js, unsafe_allow_html=True)

    # ------------------ INPUT ------------------
    user_input = st.text_input(
        "Describe symptoms or ask a first-aid question...",
        key="user_input",
        placeholder="e.g., I cut my finger and it's bleeding. What should I do?",
    )

    send = st.button("Send", type="primary")

    if send and user_input.strip():
        question = user_input.strip()

        # 1. 保存用户消息
        st.session_state.messages.append({"role": "user", "content": question})

        # 2. 调后端接口
        try:
            with st.spinner("Assistant is thinking..."):
                res = requests.post(API_URL, json={"question": question}, timeout=60)
                res.raise_for_status()
                data = res.json()
        except Exception as e:
            answer = f"❌ Error from backend：{e}"
            docs = []
        else:
            answer = data.get("answer", "⚠️ Backend did not return 'answer'")
            docs = data.get("retrieved_docs", [])

        # 3. 保存机器人回复 + 文档
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.docs = docs


with docs_col:
    st.subheader("📚 Retrieved Documents")

    docs = st.session_state.docs or []

    if not docs:
        st.info("No documents found yet. Try asking a question!")
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
