# MediPredict — Streamlit Student Project

A polished, responsive Streamlit conversion of the uploaded MediPredict HTML prototype.

## Features
- Dashboard and quick overview
- Symptom overlap checker with transparent demo ranking (not clinical probability)
- Optional AI health-education chat using OpenAI API
- BMI, blood pressure and glucose log with simple trend visualization
- Medicine list planner (no push notifications)
- Searchable learning library
- Emergency and first-aid information
- Session history, profile and JSON export

## Run locally (Windows)
1. Install Python 3.10 or newer.
2. Extract this folder and open Command Prompt / PowerShell inside it.
3. Create a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Start the app:
   ```powershell
   streamlit run app.py
   ```
6. Open the local URL printed in the terminal (usually http://localhost:8501).

## Enable AI chat (optional)
Create `.streamlit/secrets.toml` and add:
```toml
OPENAI_API_KEY = "your_api_key_here"
```
Never commit `secrets.toml` or put API keys directly in `app.py`. Without a key, the app still runs; AI features show a setup message.

## Host on Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Go to https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select your repository, branch, and `app.py`.
4. In **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "your_api_key_here"
   ```
   This is optional; skip if you do not want AI chat.
5. Deploy. Share the resulting `*.streamlit.app` URL with your college.

## Important limitations
- This is an educational demo, not a validated medical product. Symptom scores are heuristic matches, not probabilities or diagnoses.
- It does not have real user authentication, secure multi-user storage, or push notifications.
- Streamlit session data may reset when the session ends or the app reruns in a new session.
- Do not enter real patient-identifiable or sensitive medical data into a public student demo.
