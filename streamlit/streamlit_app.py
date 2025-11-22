import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="First Aid Assistant", page_icon="🚑", layout="wide")

st.markdown(
    "<h1 style='text-align:center; color:#d32f2f;'>🚑 First Aid Assistant</h1>",
    unsafe_allow_html=True
)

# 初始化 docs
if "docs" not in st.session_state:
    st.session_state.docs = []


# ---------------- HTML UI（注意三引号完全封闭） ----------------
html_code = """
<div id="chat-wrapper" style="
    width: 100%;
    height: 650px;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #ddd;
">

    <div id="chat-container" style="
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
    "></div>

    <div style="
        padding: 15px;
        border-top: 1px solid #ddd;
        display: flex;
        background: #fafafa;
    ">
        <input id="input-box" placeholder="Describe symptoms..." 
            style="
                flex: 1;
                padding: 14px;
                border-radius: 10px;
                border: 1px solid #ccc;
                font-size: 16px;
            ">
        <button onclick="send()" 
            style="
                margin-left: 10px;
                padding: 14px 20px;
                background: #d32f2f;
                color: white;
                border-radius: 10px;
                border: none;
                font-weight: bold;
                cursor: pointer;
            ">
            Send
        </button>
    </div>
</div>

<script>
const API_URL = "https://pac-games-differ-darwin.trycloudflare.com/ask";

function scrollBottom() {
    const container = document.getElementById("chat-container");
    container.scrollTop = container.scrollHeight;
}

function addUserMessage(text) {
    const chat = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.style.maxWidth = "70%";
    div.style.margin = "8px 0";
    div.style.padding = "12px";
    div.style.borderRadius = "14px";
    div.style.background = "#e8e8e8";
    div.style.alignSelf = "flex-end";
    div.innerText = text;
    chat.appendChild(div);
    scrollBottom();
}

function addBotMessage(text) {
    const chat = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.style.maxWidth = "70%";
    div.style.margin = "8px 0";
    div.style.padding = "12px";
    div.style.borderRadius = "14px";
    div.style.background = "#f5f5f5";
    div.style.borderLeft = "4px solid #d32f2f";
    div.innerText = text;
    chat.appendChild(div);
    scrollBottom();
}

async function send() {
    const input = document.getElementById("input-box");
    const text = input.value.trim();
    if (!text) return;

    addUserMessage(text);
    input.value = "";

    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: text})
    });
    const data = await res.json();

    addBotMessage(data.answer || "No response");

    window.parent.postMessage(
        {type: "docs", payload: data.retrieved_docs || []},
        "*"
    );
}
</script>
"""

components.html(html_code, height=750, scrolling=True)


# JS → Streamlit 桥
st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "docs") {
        const docs = event.data.payload;
        window.parent.postMessage(
            {type: "streamlit:setSessionState", key: "docs", value: docs},
            "*"
        );
        window.location.reload();
    }
});
</script>
""", unsafe_allow_html=True)


# ---------------- 显示 Docs ----------------
st.subheader("📚 Retrieved Documents")

docs = st.session_state.docs
for i, d in enumerate(docs, start=1):
    with st.expander(f"Document {i} (score={d['score']:.4f})"):
        st.markdown(
            f"""
            <div style='background:#fff;padding:12px;border-radius:10px;border:1px solid #eee;'>
                <strong>Q:</strong> {d['q']}<br><br>
                <strong>A:</strong> {d['a']}
            </div>
            """,
            unsafe_allow_html=True,
        )
