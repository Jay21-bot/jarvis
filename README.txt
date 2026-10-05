JARVIS - run options (Python 3.13, Windows)

1) Install once:        py -3.13 -m pip install -r requirements.txt
2) Web page (new UI):   py -3.13 server.py     -> open http://127.0.0.1:5000
3) Streamlit UI:        py -3.13 -m pip install streamlit
                        py -3.13 -m streamlit run app.py
4) Voice only:          py -3.13 main.py

API key: API_KEY in askai.py is already filled in. Alternatively set the
GEMINI_API_KEY environment variable and change API_KEY to "PASTE_YOUR_KEY_HERE".
