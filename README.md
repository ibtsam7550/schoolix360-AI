# Schoolix360 AI — Stylish Student Edition

This version starts from the original `Schoolix360-English-Starter.zip` and uses only the content already inside its `Sections.json` file: 22 topics across:

- Unit 1: The Saviour of Mankind
- Unit 2: Patriotism
- Unit 3: Daffodils

No additional units, reviews, grammar/composition book sections, or external textbook content were added.

## UI redesign
The app now has a responsive, mobile-friendly teal study-room interface inspired by the supplied Schoolix360 screenshot:

- branded header and hero panel
- three summary cards
- clearer student navigation
- large touch-friendly controls
- dark/light theme-aware cards and metrics
- styled topic and source panels
- Urdu answer styling
- reduced-motion support and small-screen layout adjustments

The CSS avoids fixed white surfaces, so dark mode does not produce invisible white text on white cards.

## Features retained
- Learn & Ask
- Quiz Practice
- Create a Test
- English, Urdu and Roman Urdu explanation choices
- keyword retrieval from the supplied notes
- supplied printed/PDF page references, marked unverified
- session-only quiz scores and downloads

## Update your existing GitHub repository
1. Extract this ZIP.
2. Upload or replace these files in the repository root:
   - `app.py`
   - `core.py`
   - `style.css`
   - `Sections.json`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
3. Commit the changes.
4. In Streamlit, reboot the app. Keep `app.py` as the main file.
5. Keep your API key in Streamlit Secrets, never in GitHub.

```toml
GEMINI_API_KEY = "YOUR_REAL_KEY"
GEMINI_MODEL = "YOUR_WORKING_MODEL_ID"
```

The code keeps the original API workflow and default model setting. If your existing model returns 503 or is unavailable, update `GEMINI_MODEL` to a model ID that works with your key.

## Local run
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Important content limitation
`Sections.json` is the exact content supplied in the starter ZIP. Its page references are unverified, and the extracted notes may contain OCR or summarization errors. Check important answers against the original book.

## Verification
The source data and backend were preserved exactly. Automated Streamlit checks confirmed the three units, three tabs, quiz scoring, test generation, and state reset. The stylesheet was reviewed for dark-mode-safe inherited surfaces. A live browser comparison could not be completed in this environment.
