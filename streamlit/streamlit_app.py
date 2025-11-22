import streamlit as st
import streamlit.components.v1 as components
import json
import requests

st.set_page_config(page_title="First Aid Assistant", page_icon="🚑", layout="wide")

# ------------------ TITLE ------------------
st.markdown(
    "<h1 style='text-align:center; color:#d32f2f;'>🚑 First Aid Assistant</h1>",
    unsafe_allow_html=True
)

# ------------------ STATE ------------------
if "docs" not in st.session_state:
    st.session_state.docs = []


# ------------------ HTML CHAT UI ------------------

html_code = f"""
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
        <input id="input-box" placeholder="Describe symptoms or ask a first-aid question..." 
            style="
                flex: 1;
                padding: 14px;
                border-radius: 10px;
                border: 1px solid #ccc;
                font-size: 16px;
            ">
        <button id="send-btn" onclick="send()" 
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
    div.style.padding = "12px 16px";
    div.style.borderRadius = "14px";
    div.style.background = "#e8e8e8";
    div.style.alignSelf = "flex-end";
    div.innerText = text;
    chat.appendChild(div);
    scrollBottom();
}

function addTyping() {
    const chat = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.id = "typing";
    div.style.maxWidth = "70%";
    div.style.margin = "8px 0";
    div.style.padding = "12px 16px";
    div.style.borderRadius = "14px";
    div.style.background = "#f5f5f5";
    div.style.borderLeft = "4px solid #d32f2f";
    div.innerHTML = "Typing...";
    chat.appendChild(div);
    scrollBottom();
}

function removeTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
}

function addBotMessage(text) {
    const chat = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.style.maxWidth = "70%";
    div.style.margin = "8px 0";
    div.style.padding = "12px 16px";
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

    addTyping();

    const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text })
    });

    const data = await res.json();
    removeTyping();

    addBotMessage(data.answer || "No response");

    // Send docs back to Streamlit
    window.parent.postMessage(
        {type: "docs", payload: data.retrieved_docs || []},
        "*"
    );
}
</script>
"""

# Render HTML UI
components.html(html_code, height=750, scrolling=True)


# ------------------ LISTEN FOR DOCS ------------------
message = st.experimental_get_query_params()

# JS → Streamlit bridge
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


# ------------------ DISPLAY RETRIEVED DOCS ------------------

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
