"""
askai.py - Gemini-powered fallback for questions JARVIS has no built-in command for.
"""

import os

from google import genai
from google.genai import types


API_KEY = ""
# -----------------------------------------------

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Replies are spoken aloud, so ask for short, plain text (no markdown/emojis).
SYSTEM_PROMPT = (
    "You are JARVIS, a helpful voice assistant. Reply in one to three short "
    "sentences of plain text. Do not use markdown, bullet points, or emojis, "
    "because your reply will be read aloud."
)

# Use the key typed above; if it was left as the placeholder, fall back to
# the GEMINI_API_KEY environment variable.
_api_key = API_KEY if API_KEY != "PASTE_YOUR_KEY_HERE" else os.getenv("GEMINI_API_KEY")
_chat = None

if _api_key:
    _client = genai.Client(api_key=_api_key)
    # A chat session remembers earlier turns, so follow-up questions work.
    _chat = _client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )


def askai(user_prompt):
    """Send a prompt to Gemini and return a short text reply."""
    if _chat is None:
        return "My Gemini API key is missing. Please add it to askai.py."

    try:
        response = _chat.send_message(user_prompt)
        return (response.text or "").strip() or "I don't have an answer for that."
    except Exception as e:
        # Print the technical details, but don't read an error dump aloud.
        print(f"[Gemini error] {e}")
        return "Sorry, I couldn't get an AI response right now."