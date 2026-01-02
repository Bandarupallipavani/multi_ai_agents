import streamlit as st
import requests
import time
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Multi AI Agent Chat", layout="wide")
st.title("Multi AI Agent Chat")

# --------------------------------------------------
# Custom CSS (IMPORTANT)
# --------------------------------------------------
st.markdown("""
<style>
/* User message - RIGHT */
div[data-testid="chat-message-user"] {
    justify-content: flex-end;
    text-align: right;
}
div[data-testid="chat-message-user"] > div {
    background-color: #1f2937;
    margin-left: auto;
    max-width: 70%;
    border-radius: 12px;
    padding: 10px;
}

/* Assistant message - LEFT */
div[data-testid="chat-message-assistant"] > div {
    background-color: #111827;
    margin-right: auto;
    max-width: 70%;
    border-radius: 12px;
    padding: 10px;
}

/* Sidebar always visible & fixed width */
section[data-testid="stSidebar"] {
    min-width: 320px !important;
    max-width: 320px !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Chat memory
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# LEFT SIDEBAR – AGENT SETTINGS
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Agent Settings")

    system_prompt = st.text_area(
        "System Prompt",
        height=120,
        placeholder="Define the behavior of your AI agent..."
    )

    selected_model = st.selectbox(
        "Select Model",
        settings.ALLOWED_MODEL_NAMES
    )

    allowed_web_search = st.checkbox("Allow web search")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --------------------------------------------------
# RIGHT SIDE – CHAT AREA
# --------------------------------------------------
st.subheader("💬 Conversation")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------
# Streaming helper
# --------------------------------------------------
def stream_text(text, delay=0.02):
    for word in text.split():
        yield word + " "
        time.sleep(delay)

# --------------------------------------------------
# Chat input (BOTTOM)
# --------------------------------------------------
user_query = st.chat_input("Type your message...")

if user_query:
    # USER MESSAGE (RIGHT)
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt,
        "messages": st.session_state.messages,
        "allow_search": allowed_web_search
    }

    try:
        # ASSISTANT RESPONSE (LEFT)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                logger.info("Sending request to backend")
                response = requests.post(
                    "http://127.0.0.1:9999/chat",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                agent_response = response.json().get("response", "")

                # Stream output
                st.write_stream(stream_text(agent_response))

        st.session_state.messages.append(
            {"role": "assistant", "content": agent_response}
        )

    except Exception as e:
        logger.exception("Frontend error")
        st.error(str(e))
