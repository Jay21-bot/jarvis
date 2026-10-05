"""
features_module.py - Speech, listening, and command handling for JARVIS.

Design rule: every command handler RETURNS the text to speak. main.py speaks
and prints it once, so nothing is said twice.
"""

import datetime
import os
import platform
import queue
import random
import re
import smtplib
import subprocess
import sys
import threading
import webbrowser
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote_plus

import psutil
import pyautogui
import pyttsx3
import requests
import speech_recognition as sr
import wikipedia

from askai import askai  # Gemini fallback for anything not handled below

recognizer = sr.Recognizer()
_calibrated = False

EXIT_WORDS = {"stop", "exit", "quit", "close", "goodbye", "bye"}

# Apps JARVIS can open (Windows). Add your own: "spoken name": "program name".
APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "command prompt": "cmd",
    "file explorer": "explorer",
    "task manager": "taskmgr",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "spotify": "spotify:",
}

# Websites JARVIS can open. Add your own: "spoken name": "https://...".
WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
}


# --------------------------------------------------------------------------
# Speech output
# --------------------------------------------------------------------------
speech_queue = queue.Queue()


def _speech_worker():
    """Background thread that speaks queued messages one at a time.

    The TTS engine is created INSIDE this thread, because pyttsx3 engines
    can misbehave when created in one thread and used in another.
    """
    engine = pyttsx3.init()
    while True:
        message = speech_queue.get()
        try:
            if message is None:
                break
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"[Speech error] {e}")
        finally:
            speech_queue.task_done()


threading.Thread(target=_speech_worker, daemon=True).start()


def say(message):
    """Queue text to be spoken (non-blocking). Empty messages are ignored."""
    if message:
        speech_queue.put(str(message))


def wait_for_speech():
    """Block until everything queued has been spoken."""
    speech_queue.join()


# --------------------------------------------------------------------------
# Speech input
# --------------------------------------------------------------------------
def listen(phrase_time_limit=6):
    """Listen once and return the recognized text, or "" if nothing usable.

    Returning "" (instead of a message like "I didn't catch that") stops
    JARVIS from treating its own error text as a command.
    """
    global _calibrated

    # Don't open the mic while JARVIS is still talking, or it hears itself.
    wait_for_speech()

    with sr.Microphone() as source:
        if not _calibrated:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            _calibrated = True
        print("Listening...")
        try:
            audio = recognizer.listen(
                source, timeout=10, phrase_time_limit=phrase_time_limit
            )
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""  # silence or unclear speech - just listen again
        except sr.RequestError:
            print("[Speech recognition service unavailable - check internet]")
            return ""


# --------------------------------------------------------------------------
# Features (each one returns the text to speak)
# --------------------------------------------------------------------------
def stop_jarvis():
    """Say goodbye, wait until it has been spoken, then exit."""
    say("Shutting down. Goodbye!")
    wait_for_speech()
    speech_queue.put(None)
    sys.exit(0)


def open_application(name):
    """Open a known app or website. Only names from APPS / WEBSITES are used,
    never raw spoken text, so a misheard word can't run a random command."""
    name = re.sub(r"^(the|my)\s+", "", name.strip())

    if name in WEBSITES:
        webbrowser.open(WEBSITES[name])
        return f"Opening {name}."

    if name in APPS:
        if platform.system() != "Windows":
            return "Opening apps is only set up for Windows."
        try:
            os.startfile(APPS[name])
            return f"Opening {name}."
        except OSError as e:
            print(f"[Open app error] {e}")
            return f"I couldn't open {name}. It may not be installed."

    return "I can't open that yet."


def play_music(song):
    """Play a song on YouTube."""
    import pywhatkit  # imported here: it needs internet just to be imported

    try:
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube."
    except Exception as e:
        print(f"[Music error] {e}")
        return "Sorry, I couldn't play that."


def send_email(to_email, subject, body):
    """Send an email using credentials from environment variables."""
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")  # For Gmail, use an App Password
    if not sender or not password:
        return "Email credentials are missing. Set EMAIL_USER and EMAIL_PASS first."

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        return "Email sent successfully."
    except Exception as e:
        print(f"[Email error] {e}")
        return "Failed to send the email."


def email_flow():
    """Collect email details, then send. The address is typed because voice
    recognition is unreliable for email addresses."""
    if not os.getenv("EMAIL_USER") or not os.getenv("EMAIL_PASS"):
        return "Email credentials are missing. Set EMAIL_USER and EMAIL_PASS first."

    to_email = input("Recipient email address: ").strip()
    if not to_email:
        return "Email cancelled."

    say("What is the subject?")
    subject = listen()
    say("What should the message say?")
    body = listen(phrase_time_limit=20)
    if not subject or not body:
        return "I didn't catch that, so I cancelled the email."

    return send_email(to_email, subject, body)


def get_weather(city=None):
    """Fetch current weather from OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = city or os.getenv("WEATHER_CITY")
    if not api_key:
        return "Weather API key is missing. Set OPENWEATHER_API_KEY first."
    if not city:
        return "Which city? Try saying: weather in Delhi."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        if response.status_code == 404:
            return f"I couldn't find a city called {city}."
        response.raise_for_status()
        data = response.json()
        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is {description}, around {temp:.0f} degrees Celsius."
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"[Weather error] {e}")
        return "I couldn't fetch the weather details."


def google_search(query):
    """Open a Google search in the browser."""
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Searching Google for {query}."


def wiki_summary(topic):
    """Short Wikipedia summary."""
    try:
        return wikipedia.summary(topic, sentences=2, auto_suggest=False)
    except wikipedia.DisambiguationError:
        return f"{topic} could mean several things. Please be more specific."
    except wikipedia.PageError:
        return f"I couldn't find a Wikipedia page for {topic}."
    except Exception as e:
        print(f"[Wikipedia error] {e}")
        return "I couldn't reach Wikipedia right now."


def take_screenshot():
    """Save a real screenshot to Pictures/Screenshots."""
    try:
        folder = Path.home() / "Pictures" / "Screenshots"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
        pyautogui.screenshot(str(path))
        return f"Screenshot saved as {path.name} in your Pictures folder."
    except Exception as e:
        print(f"[Screenshot error] {e}")
        return "I couldn't take a screenshot."


def control_system(command):
    """System status and power commands."""
    if command == "battery":
        battery = psutil.sensors_battery()
        if battery is None:  # desktops have no battery
            return "I couldn't detect a battery on this device."
        state = "charging" if battery.power_plugged else "not charging"
        return f"Battery is at {battery.percent:.0f} percent and {state}."

    if command == "cpu usage":
        return f"CPU usage is at {psutil.cpu_percent(interval=1):.0f} percent."

    if command == "memory usage":
        return f"Memory usage is at {psutil.virtual_memory().percent:.0f} percent."

    if command in ("shutdown", "restart"):
        if platform.system() != "Windows":
            return "Shutdown and restart are only set up for Windows."
        # Speech recognition can mishear, so always confirm first.
        say(f"Are you sure you want to {command}? Say yes to confirm.")
        if "yes" not in listen():
            return "Okay, cancelled."
        flag = "/s" if command == "shutdown" else "/r"
        subprocess.run(["shutdown", flag, "/t", "5"])
        return f"Okay, {command} in 5 seconds."

    return "I can't perform that action yet."


def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts!",
    ]
    return random.choice(jokes)


# --------------------------------------------------------------------------
# Command routing
# --------------------------------------------------------------------------
def _has(text, *phrases):
    """True if any phrase appears as whole words (so 'time' won't match 'sometimes')."""
    return any(re.search(rf"\b{re.escape(p)}\b", text) for p in phrases)


def process_command(text):
    """Match the spoken text to a feature and return the reply to speak."""
    text = text.lower().strip()
    if not text:
        return ""

    if text in EXIT_WORDS:
        stop_jarvis()

    if re.match(r"(hello|hi|hey)\b", text):
        return "Hello! How can I help you?"

    # "why ..." questions get a short, easy explanation from Gemini.
    if re.match(r"why\b", text):
        return askai(text + ". Explain this in a short and easy way.")

    # "open notepad", "open youtube", ...
    match = re.match(r"(?:please )?open (.+)", text)
    if match:
        return open_application(match.group(1))

    if _has(text, "joke"):
        return tell_joke()

    if _has(text, "screenshot"):
        return take_screenshot()

    if _has(text, "weather"):
        match = re.search(r"weather (?:in|for|at) (.+)", text)
        return get_weather(match.group(1).strip() if match else None)

    match = re.search(r"wikipedia (?:for |about )?(.+)", text)
    if match:
        return wiki_summary(match.group(1).strip())

    match = re.search(r"search(?: google)?(?: for)? (.+)", text)
    if match:
        return google_search(match.group(1).strip())

    match = re.match(r"play (.+)", text)
    if match:
        song = match.group(1).replace(" on youtube", "").strip()
        song = re.sub(r"^music\s+", "", song)  # "play music believer" -> "believer"
        if song in {"music", "a song", "song", "something"}:
            return "Which song? Say play, followed by the song name."
        return play_music(song)

    if _has(text, "send email", "send an email", "send a mail"):
        return email_flow()

    if _has(text, "battery"):
        return control_system("battery")
    if _has(text, "cpu usage", "cpu"):
        return control_system("cpu usage")
    if _has(text, "memory usage", "memory", "ram"):
        return control_system("memory usage")
    if re.search(r"\bshut ?down\b", text):
        return control_system("shutdown")
    if _has(text, "restart"):
        return control_system("restart")

    if _has(text, "time"):
        return f"The current time is {datetime.datetime.now():%I:%M %p}."
    if _has(text, "date", "today"):
        return f"Today is {datetime.datetime.now():%A, %d %B %Y}."

    # Nothing matched: let Gemini answer.
    return askai(text)