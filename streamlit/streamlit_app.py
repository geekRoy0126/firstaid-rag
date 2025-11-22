import streamlit as st
import requests
import json

API_URL = "https://pac-games-differ-darwin.trycloudflare.com/ask"

st.set_page_config(page_title="First Aid Assistant", page_icon="🚑", layout="wide")

# ------------------ STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  
if "docs" not in st.session_state:
    st.session_state.docs = []

# ------------------ CSS（修复空白问题 + WhatsApp 风） ------------------
chat_css = """
<style>
body {
    background-color: #e5ddd5 !important;
}

/* 左侧 Chat 区域整体收紧，不再被撑开 */
.block-container {
    padding-top: 1rem !important;
}

/* 聊天容器 */
.chat-box {
    background: #fafafa;
    border-radius: 12px;
    border: 1px solid #ddd;
    height: 450px;          
    padding: 12px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

/* 通用气泡 */
.chat-bubble {
    padding: 10px 14px;
    border-radius: 14px;
    max-width: 60%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0px 1px 1px rgba(0,0,0,0.1);
}

/* 用户（右） */
.user-bubble {
    background: #dcf8c6;
    margin-left: auto;
}

/* AI（左） */
.bot-bubble {
    background: #ffffff;
    margin-right: auto;
}

/* 标题 */
.main-title {
    text-align: center;
    font-weight: bold;
    color: #075E54;
    font-size: 32px;
    margin-bottom: 10px;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("<h1 class='main-title'>🚑 First Aid Assistant</h1>", unsafe_allow_html=True)

# ------------------ LAYOUT ------------------
chat_col, docs_col = st.columns([2, 1])

with chat_col:

    st.subheader("💬 Chat")

    # ------------- 聊天窗口（无空白、强制贴顶） -------------
    chat_box = st.container()
    with chat_box:
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            st.markdown(
                f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # 自动滚动到底部
    scroll_js = """
    <script>
        const box = window.parent.document.getElementsByClassName('chat-box')[0];
        if (box) { box.scrollTop = box.scrollHeight; }
    </script>
    """
    st.markdown(scroll_js, unsafe_allow_html=True)

    # ------------------ INPUT ------------------
    user_input = st.text_input(
        "Describe symptoms or ask a first-aid question...",
        key="user_input",
        placeholder="e.g., I cut my finger and it's bleeding.",
    )
    send = st.button("Send", type="primary")

    if send and user_input.strip():
        question = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": question})

        try:
            with st.spinner("Assistant is thinking..."):
                res = requests.post(API_URL, json={"question": question}, timeout=60)
                res.raise_for_status()
                data = res.json()
        except Exception as e:
            answer = f"❌ Backend error: {e}"
            docs = []
        else:
            answer = data.get("answer", "⚠️ Backend did not return 'answer'")
            docs = data.get("retrieved_docs", [])

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.docs = docs


# ------------------ DOCUMENTS ------------------
with docs_col:
    st.subheader("📚 Retrieved Documents")

    docs = st.session_state.docs or []

    if not docs:
        st.info("No documents found yet. Ask something!")
    else:
        for i, d in enumerate(docs, start=1):
            score = d.get("score", 0.0)
            q = d.get("q", "")
            a = d.get("a", "")
            with st.expander(f"Document {i} (score={score:.4f})"):
                st.markdown(
                    f"""
                    <div style="background:#fff; padding:12px; 
                                border-radius:10px; border:1px solid #eee;">
                        <strong>Q:</strong> {q}<br><br>
                        <strong>A:</strong> {a}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
