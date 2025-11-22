import streamlit as st
import requests
import json

API_URL = "https://pac-games-differ-darwin.trycloudflare.com/ask"

st.set_page_config(page_title="First Aid RAG Assistant", page_icon="🚑", layout="centered")

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
.doc-block {
    background: #fff;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #eee;
    margin-bottom: 8px;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚑 First Aid RAG Assistant</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    bubble = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {bubble}'>{msg['content']}</div>", unsafe_allow_html=True)

question = st.text_area("Your question:", height=80)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            try:
                res = requests.post(API_URL, json={"question": question})

                if res.status_code != 200:
                    st.error(f"❌ API 状态码错误：{res.status_code}")
                else:
                    try:
                        data = res.json()
                        answer = data.get("answer", "")
                        docs = data.get("retrieved_docs", [])

                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.session_state.docs = docs
                        st.rerun()

                    except json.JSONDecodeError:
                        st.error("❌ API 返回的不是 JSON，请检查 Cloudflare Tunnel 是否在线。")

            except Exception as e:
                st.error(f"❌ API 请求失败：{e}")

st.subheader("📚 Retrieved Documents")

if "docs" in st.session_state:
    for i, d in enumerate(st.session_state.docs, start=1):
        with st.expander(f"Document {i} (score={d['score']:.4f})"):
            st.markdown(
                f"""
                <div class='doc-block'>
                <strong>Q:</strong> {d['q']}<br><br>
                <strong>A:</strong> {d['a']}
                </div>
                """,
                unsafe_allow_html=True,
            )
