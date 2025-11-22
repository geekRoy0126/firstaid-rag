import streamlit as st
import requests
import json

# ------------------ Cloudflare Tunnel ------------------
API_URL = "https://map-disclosure-honey-howard.trycloudflare.com/ask"

st.set_page_config(page_title="First Aid RAG Assistant", page_icon="🚑", layout="centered")

# ------------------ Dark Mode CSS ------------------
dark_css = """
<style>
/* 全局背景 */
body, .main {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

/* 输入框背景 */
textarea, input {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border-radius: 10px !important;
    border: 1px solid #30363d !important;
}

/* 按钮样式 */
button[kind="primary"] {
    background-color: #238636 !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    border: none !important;
}
button[kind="primary"]:hover {
    background-color: #2ea043 !important;
}

/* 标题 */
.title {
    text-align: center;
    margin-top: 30px;
    color: #58a6ff;
    font-weight: 700;
}

/* 聊天气泡基础样式 */
.chat-bubble {
    padding: 14px 18px;
    border-radius: 18px;
    margin: 10px 0;
    max-width: 80%;
    line-height: 1.6;
    font-size: 17px;
    animation: fadeIn 0.3s ease;
}

/* 用户气泡（右对齐） */
.user-bubble {
    background: #238636;
    color: #ffffff;
    margin-left: auto;
    border: 1px solid #2ea043;
}

/* AI 气泡（左对齐） */
.ai-bubble {
    background: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    margin-right: auto;
}

/* 文档块 */
.doc-block {
    background: #161b22;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #30363d;
    margin-bottom: 10px;
    color: #e6edf3;
}

/* 动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ------------------ 页面标题 ------------------
st.markdown("<h1 class='title'>🚑 First Aid RAG Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b949e;'>Ask any first-aid related question. Powered by your local RAG system.</p>", unsafe_allow_html=True)

# ------------------ 聊天历史 ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示历史聊天
for msg in st.session_state.messages:
    bubble = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {bubble}'>{msg['content']}</div>", unsafe_allow_html=True)

# ------------------ 输入栏 ------------------
question = st.text_area("Your question:", height=80, key="input_area")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # 用户消息
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            try:
                res = requests.post(API_URL, json={"question": question}, timeout=15)

                if res.status_code != 200:
                    st.error(f"❌ API Error: {res.status_code}")
                    st.error(res.text)
                else:
                    data = res.json()

                    answer = data.get("answer", "No answer returned.")
                    docs = data.get("retrieved_docs", [])

                    # AI 回复
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.session_state.docs = docs

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error calling API: {e}")

# ------------------ RAG 文档显示区 ------------------
st.subheader("📚 Retrieved Documents")

if "docs" in st.session_state:
    for i, d in enumerate(st.session_state.docs, start=1):
        with st.expander(f"Document {i}  (score={d['score']:.4f})"):
            st.markdown(
                f"""
                <div class='doc-block'>
                    <strong>Q:</strong> {d['q']}<br><br>
                    <strong>A:</strong> {d['a']}
                </div>
                """,
                unsafe_allow_html=True,
            )


