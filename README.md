# Schoolix360 AI — Grade 9 English

A hackathon prototype for learning, asking questions, practising quizzes, and generating MCQ tests. Uses Gemini and keyword-based TF-IDF retrieval over supplied English study notes.

## Included coverage
- Unit 1: The Saviour of Mankind
- Unit 2: Patriotism
- Unit 3: Daffodils

The 22 supplied sections contain summaries and grammar notes, not a complete textbook transcription. The original English PDF was not in the supplied ZIP. Content and page references remain unverified; compare them with your actual textbook before claiming textbook accuracy or curriculum alignment. Sections.json is preserved as supplied.

## Deploy using only a browser
1. Extract this ZIP on your computer.
2. Open your existing GitHub repository. Choose Add file > Upload files.
3. Upload app.py, core.py, Sections.json, requirements.txt and README.md into the repository root, not a subfolder. Upload .gitignore too if visible. If requirements.txt or README.md already exists, replace it with this version.
4. Commit changes. Never upload your real API key.
5. Open https://share.streamlit.io/ and sign in with GitHub.
6. Click Create app, choose your repository and branch (normally main), and set the main file to app.py.
7. Open Advanced settings. Choose Python 3.11 if available. Paste these settings into Secrets, replacing the key placeholder:

```toml
GEMINI_API_KEY = "PASTE_YOUR_REAL_KEY_HERE"
GEMINI_MODEL = "gemini-3.8-flash"
```

The model above is the example in Google's documentation checked during preparation. Model access and quota depend on your account. If unavailable, use an exact text model ID supported by the Interactions API and available to your account. Change GEMINI_MODEL in Streamlit Secrets; no code edit is needed.

8. Save and Deploy. Wait for installation and open the app URL.
9. Select Unit 2, Gerunds, Infinitives, and Participles. Click Teach me this topic.
10. Ask "What is a gerund?" and inspect the study notes expander.
11. Generate a quiz, complete it and submit. Generate a practice test and download both text files.
12. Open the public app link in a signed-out browser and on a phone before submitting.

## How it works
Learn retrieves the selected topic's note. Ask ranks notes in the selected unit using TF-IDF keyword similarity and sends up to three positive matches to Gemini with source IDs. A prompt instructs Gemini to stay within the notes and acknowledge missing support. Source references are displayed from the stored records. Keyword overlap does not guarantee that a passage answers the question; review important outputs.

Quiz/test generation uses the selected topic's note. JSON structure, option count, answer index and question count are validated. Marking is deterministic against the generated answer key, but the key's factual correctness requires review. Generated tests contain 5 or 10 MCQs worth one mark each. Downloads are UTF-8 text, not PDFs. Open them in Word or Google Docs to export PDFs.

## Local run (optional)
Use Python 3.11 or newer:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For local credentials create .streamlit/secrets.toml using the settings above. Never commit that file. Use a fresh project directory; the previous Extract.py, BuildIndex.py, Retrieve.py and Api.py are not used.

## Troubleshooting
- ModuleNotFoundError: confirm this package's requirements.txt is beside app.py; use Streamlit Manage app > Reboot after correcting it.
- Sections.json missing: filename is case-sensitive and must be beside core.py.
- API request failed: check key validity, model access, Google AI Studio usage/quota, and the configured model ID. Do not share raw credentials or unredacted logs.
- No search match: use English keywords and choose the appropriate unit. Urdu/Roman Urdu are output-language options, not multilingual retrieval.
- Invalid quiz format: generate again; malformed assessments are rejected rather than displayed.
- Scores disappear: session-only storage is intentional. Changing unit, topic or language starts fresh work.

## Five-minute demo
0:00–0:35 Explain the problem and target students.
0:35–1:40 Teach one grammar topic and show Urdu or Roman Urdu explanation.
1:40–2:25 Ask a question and show the retrieved notes; explain their verification status.
2:25–3:20 Complete a quiz and show score and feedback.
3:20–4:05 Generate and download a test and separate key.
4:05–5:00 Explain your measured impact and limitations.

## Submission checklist
- Live app URL, tested outside your own logged-in browser.
- GitHub repository URL and this README.
- Five-minute demonstration video.
- Presentation: problem, students, solution, retrieval workflow, measured results, next steps.
- Impact assessment with actual results. Record who tested, task, baseline time, app time and accuracy. Time saved percentage = (baseline time - app time) / baseline time * 100. Do not invent pilot results.

## Limits and next steps
No accounts, database, permanent progress, full-book coverage, handwritten marking, or official board validation. AI can make mistakes. Session throttling is not a global spending cap; configure account quota/budget controls for public use. Students should not enter personal information; questions and relevant notes are sent to Google for generation.

## Verification status
Python syntax, note retrieval, quiz parser, separate test export, Streamlit startup and quiz submission were checked locally. A mocked API response verified a complete 5/5 quiz submission; this does not verify live AI output quality. Live Gemini generation and cloud deployment require your account and have not been verified by the authoring assistant. Follow the deployment checks above before submitting.
