"""
app.py - Streamlit web interface for JARVIS.

Run with:   py -3.13 -m streamlit run app.py
Keep this file in the same folder as features_module.py and askai.py.
"""

import re

import streamlit as st

from features_module import EXIT_WORDS, listen, process_command, say, send_email

st.set_page_config(page_title="JARVIS", page_icon="🤖")
st.title("🤖 JARVIS")
st.caption("Type below, or press 🎤 Speak in the sidebar.")

GREETING = "Jarvis is online. How can I help you?"

QUICK_COMMANDS = {
    "🕒 Time": "what time is it",
    "😄 Joke": "tell me a joke",
    "📸 Screenshot": "take a screenshot",
    "🔋 Battery": "battery",
    "💻 CPU usage": "cpu usage",
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]


def run_command(text):
    """Send the text to JARVIS and return the reply (never raises)."""
    clean = text.lower().strip()

    # In the web app, closing is done from the terminal, not by voice/text.
    if clean in EXIT_WORDS:
        return "To close JARVIS, press Ctrl+C in the terminal window."

    # The terminal email flow uses input(), which can't work in a web page.
    if re.search(r"\bsend (?:an |a )?(?:email|mail)\b", clean):
        return "Please use the Email form in the sidebar."

    try:
        return process_command(text) or "I'm not sure how to help with that."
    except Exception as e:
        print(f"[Error] {e}")
        return "Sorry, something went wrong."


# ---------------------------------------------------------------- sidebar
st.sidebar.header("Controls")
speak_replies = st.sidebar.toggle("Speak replies aloud", value=True)

user_text = None

if st.sidebar.button("🎤 Speak", use_container_width=True, type="primary"):
    with st.spinner("Listening... speak now"):
        heard = listen()
    if heard:
        user_text = heard
    else:
        st.sidebar.warning("I didn't catch that. Try again.")

st.sidebar.divider()
st.sidebar.subheader("Quick commands")
for label, command in QUICK_COMMANDS.items():
    if st.sidebar.button(label, use_container_width=True):
        user_text = command

st.sidebar.divider()
with st.sidebar.expander("✉️ Send an email"):
    with st.form("email_form", clear_on_submit=True):
        to_email = st.text_input("To")
        subject = st.text_input("Subject")
        body = st.text_area("Message")
        submitted = st.form_submit_button("Send")
    if submitted:
        if to_email and subject and body:
            st.info(send_email(to_email, subject, body))
        else:
            st.warning("Please fill in all three fields.")

st.sidebar.divider()
if st.sidebar.button("🗑️ Clear chat", use_container_width=True):
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.rerun()

# ------------------------------------------------------------------- chat
typed = st.chat_input("Type a command or question...")
if typed:
    user_text = typed

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.spinner("Thinking..."):
        reply = run_command(user_text)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    if speak_replies:
        say(reply)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])



# py -3.13 -m streamlit run app.py