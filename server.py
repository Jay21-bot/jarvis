"""
server.py - Flask backend for the JARVIS HTML interface.

Run with:   py -3.13 server.py      then open http://127.0.0.1:5000
Folder layout:
    server.py, features_module.py, askai.py
    templates/index.html
"""

import re

from flask import Flask, jsonify, render_template, request

from features_module import EXIT_WORDS, listen, process_command, say, send_email

app = Flask(__name__)


def run_command(text):
    """Same safety rules as app.py: never raises, no terminal-only flows."""
    clean = text.lower().strip()
    if clean in EXIT_WORDS:
        return "To close JARVIS, press Ctrl+C in the terminal window."
    if re.search(r"\bsend (?:an |a )?(?:email|mail)\b", clean):
        return "Please use the Email button in the top bar."
    try:
        return process_command(text) or "I'm not sure how to help with that."
    except Exception as e:
        print(f"[Error] {e}")
        return "Sorry, something went wrong."


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/command")
def api_command():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(reply="Type or say a command first.")
    reply = run_command(text)
    if data.get("speak", True):
        say(reply)
    return jsonify(reply=reply)


@app.post("/api/listen")
def api_listen():
    heard = listen()
    return jsonify(text=heard)


@app.post("/api/email")
def api_email():
    data = request.get_json(silent=True) or {}
    to, subject, body = (data.get(k, "").strip() for k in ("to", "subject", "body"))
    if not (to and subject and body):
        return jsonify(reply="Please fill in all three fields."), 400
    return jsonify(reply=send_email(to, subject, body))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
