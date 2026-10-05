# 🤖 JARVIS: AI Voice Assistant

JARVIS is a Python voice assistant you can talk to or type to. It has a web interface built with HTML, CSS and JavaScript on a Flask backend, plus an optional Streamlit app and a voice-only terminal mode. Anything without a built-in command is answered by Google Gemini.

## ✨ Features

- 🎤 Voice commands and spoken replies
- 💬 Chat-style web interface with an animated arc-reactor orb
- 🧠 Gemini AI answers for general questions
- 🌐 Open websites and apps, search Google, play songs on YouTube
- 📚 Wikipedia summaries and weather reports
- 📸 Screenshots, battery, CPU and memory status
- ✉️ Send emails from the web interface
- 🌗 Light and dark themes

## 🛠️ Tech Stack

Python, Flask, Streamlit, Google Gemini API, SpeechRecognition, pyttsx3, HTML, CSS, JavaScript

## 📁 Project Structure

```
jarvis/
├── server.py            # Flask backend for the web interface
├── templates/
│   └── index.html       # Web UI (HTML, CSS, JS)
├── features_module.py   # Commands, speech input and output
├── askai.py             # Gemini AI fallback
├── main.py              # Voice-only terminal mode
├── app.py               # Streamlit interface
└── requirements.txt
```

## 🚀 Setup

1. Clone the repo
```bash
   git clone https://github.com/your-username/jarvis.git
   cd jarvis
```

2. Install the libraries
```bash
   pip install -r requirements.txt
```
   If you want the Streamlit version, also run `pip install streamlit`.

3. Add your Gemini API key (get one at https://aistudio.google.com)
```bash
   # Windows
   set GEMINI_API_KEY=your_key_here

   # macOS / Linux
   export GEMINI_API_KEY=your_key_here
```

## ▶️ Run

```bash
python server.py          # web interface at http://127.0.0.1:5000
python main.py            # voice-only mode
streamlit run app.py      # Streamlit interface
```

## 🗣️ Example Commands

- "What time is it"
- "Tell me a joke"
- "Open YouTube"
- "Play believer"
- "Weather in Delhi"
- "Wikipedia Albert Einstein"
- "Search python tutorials"
- "Take a screenshot"
- "Battery" / "CPU usage" / "Memory usage"
- "Why is the sky blue" (answered by Gemini)

## 🔧 Optional Environment Variables

| Variable | Used for |
|---|---|
| `GEMINI_API_KEY` | Gemini AI answers |
| `EMAIL_USER` | Sender Gmail address |
| `EMAIL_PASS` | Gmail App Password |
| `OPENWEATHER_API_KEY` | Weather reports |
| `WEATHER_CITY` | Default city for weather |

## ⚠️ Notes

- App opening, shutdown and restart are set up for Windows only.
- Voice input needs a microphone and PyAudio. If PyAudio fails to install on Python 3.13, try Python 3.12.
- Never commit your API keys. Keep them in environment variables.

## 📄 License

MIT License
