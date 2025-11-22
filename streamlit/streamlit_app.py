import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="First Aid Assistant", page_icon="🚑", layout="wide")

st.markdown(
    "<h1 style='text-align:center; color:#d32f2f;'>🚑 First Aid Assistant</h1>",
    unsafe_allow_html=True
)

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>First Aid Chatbot</title>

<style>
    body {
        background: #ffffff;
        font-family: Inter, sans-serif;
        color: #333333;
        margin: 0;
        padding: 0;
    }

    #chat-container {
        height: 600px;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
    }

    .bubble {
        max-width: 70%;
        padding: 14px 18px;
        margin: 10px 0;
        border-radius: 16px;
        font-size: 16px;
        line-height: 1.6;
        opacity: 0;
        animation: fadeIn 0.4s forwards, slideUp 0.4s ease-out;
    }

    @keyframes fadeIn {
        to { opacity: 1; }
    }
    @keyframes slideUp {
        from { transform: translateY(12px); }
        to { transform: translateY(0); }
    }

    .user {
        background: #e8e8e8;
        color: #333333;
        margin-left: auto;
        border: 1px solid #cccccc;
        animation: slideRight 0.4s ease-out;
    }

    .bot {
        background: #f5f5f5;
        border-left: 4px solid #d32f2f;
        border: 1px solid #dddddd;
        color: #333333;
        animation: slideLeft 0.4s ease-out;
    }

    @keyframes slideRight {
        from { transform: translateX(40px); }
        to { transform: translateX(0); }
    }
    @keyframes slideLeft {
        from { transform: translateX(-40px); }
        to { transform: translateX(0); }
    }

    #input-box {
        width: 80%;
        padding: 14px;
        background: #fafafa;
        border: 1px solid #cccccc;
        color: #333333;
        border-radius: 12px;
        outline: none;
        font-size: 16px;
    }
    #input-box:focus {
        border-color: #d32f2f;
        box-shadow: 0 0 6px rgba(211, 47, 47, 0.3);
    }

    #send-btn {
        padding: 14px 22px;
        background: #d32f2f;
        border: none;
        color: white;
        font-size: 16px;
        border-radius: 12px;
        margin-left: 10px;
        cursor: pointer;
        font-weight: bold;
    }
    #send-btn:hover {
        background: #e04343;
    }

    /* typing dots */
    @keyframes blink {
        0% { opacity: .2; }
        20% { opacity: 1; }
        100% { opacity: .2; }
    }
    .typing {
        display: inline-block;
        width: 50px;
    }
    .typing span {
        animation-name: blink;
        animation-duration: 1.4s;
        animation-iteration-count: infinite;
        animation-fill-mode: both;
    }
    .typing span:nth-child(2) {
        animation-delay: .2s;
    }
    .typing span:nth-child(3) {
        animation-delay: .4s;
    }

</style>
</head>

<body>

<div id="chat-container"></div>

<div style="padding: 20px; display: flex; justify-content:center;">
    <input id="input-box" placeholder="Describe symptoms or ask a first-aid question...">
    <button id="send-btn" onclick="send()">Send</button>
</div>

<script>
const API_URL = "https://map-disclosure-honey-howard.trycloudflare.com/ask";

const chatContainer = document.getElementById("chat-container");

function scrollBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "bubble user";
    div.textContent = text;
    chatContainer.appendChild(div);
    scrollBottom();
}

function addTypingBubble() {
    const div = document.createElement("div");
    div.className = "bubble bot";
    div.id = "typing";
    div.innerHTML = "<div class='typing'><span>●</span><span>●</span><span>●</span></div>";
    chatContainer.appendChild(div);
    scrollBottom();
}

function removeTypingBubble() {
    const node = document.getElementById("typing");
    if (node) node.remove();
}

function addBotMessageTextSlow(text) {
    const div = document.createElement("div");
    div.className = "bubble bot";
    chatContainer.appendChild(div);

    let i = 0;
    function typeWriter() {
        if (i < text.length) {
            div.innerHTML += text.charAt(i);
            i++;
            scrollBottom();
            setTimeout(typeWriter, 15);
        }
    }
    typeWriter();
}

async function send() {
    const input = document.getElementById("input-box");
    const text = input.value.trim();
    if (!text) return;

    addUserMessage(text);
    input.value = "";

    addTypingBubble();

    const response = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: text})
    });

    const data = await response.json();
    removeTypingBubble();

    addBotMessageTextSlow(data.answer || "No response.");
}
</script>

</body>
</html>
"""

components.html(html_code, height=750, scrolling=True)

