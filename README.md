# Update 2.1: dark-mode and model setup fixes

Read FIXES.md first. Only app.py and core.py need replacing on an existing v2 deployment.

# Schoolix360 AI — Student Edition 2.1

A textbook-only English learning companion for students who cannot afford extra academy support. Built from the supplied English-book.txt and the supplied Taleem360 pairing-scheme PDF. This is an upgrade of the original Streamlit starter, not a separate website platform.

## What is included
- Redesigned responsive Overview, Learn & ask, Practice, My progress and Practice paper workspaces.
- All 11 English textbook units and both reviews: 164 content pages, 170 source chunks.
- Simple English, Urdu and Roman Urdu explanations. Urdu-script questions are translated into an English search query before retrieval (two API calls). Roman Urdu search is best done with English keywords or by selecting a page.
- Cached TF-IDF retrieval and programmatically validated source IDs. Expand the evidence behind an answer.
- Five-question checks, deterministic marking against the AI answer key, explanations and targeted fresh questions based on the last attempt's mistakes.
- Anonymous session progress; export/import a JSON file to continue later. No hosted database or student accounts required.
- A 37-mark textbook-only paper subset, generated section by section, with separate question-paper and answer-guide PDFs.
- Bundled fonts and right-to-left shaping for Urdu PDF text.

## The scope you requested
Only the English textbook is used. Grammar, vocabulary, comprehension and writing exercises physically present in that book remain in scope. The separate English Grammar and Composition 9–10 book is not used. There are no teacher accounts or teacher editing/review workflows.

## Important source limitations
English-book.txt contains noisy OCR, including watermark interference and garbled lines. Text was segmented at its original form-feed page breaks, without inventing corrections. Four front-matter pages precede printed page 1; printed page labels are inferred by subtracting four from the OCR page position. Unit boundaries agree with the OCR contents table and chapter openings, but the original English book PDF was not supplied. Therefore page labels and quotations are NOT visually verified. The app says so in its source panel. Inspect the original textbook when checking an answer.

The model is instructed not to reconstruct unreadable passages. Citation validation verifies source IDs, not the factual entailment of every sentence. Translation passages and quoted poetry in papers must match their cited OCR excerpts, but OCR itself can be wrong. An original readable PDF would allow stronger verification and correction.

## Paper scope and marks
The supplied scheme is a Taleem360 document dated 9 April 2026; it has not been independently verified as an official board notification.

Included:
- Q1 B spellings: 4 x 1 = 4, split 2/2 across the two unit groups.
- Q1 C meanings: 5 x 1 = 5, split 2/3 across the groups.
- Q2 A short answers: offer 5, attempt 3 x 2 = 6.
- Q2 B play: offer 2, attempt 1 x 4 = 4.
- Q3 translation: offer 3, attempt 2 x 4 = 8; two source paragraphs from units 1/2/4/6 and one from unit 9.
- Q4 poetry: offer two alternatives (summary or stanza), attempt one = 5.
- Q5 words/phrases: offer 8, attempt 5 x 1 = 5.
- Total = 37.

Excluded: Q1 A, mixed-source Q1 D, and Q6–Q9. The supplied full scheme totals 75; this app does NOT claim to generate a complete official 75-mark paper. No duration is invented for the custom subset. Paper generation excludes units 5, 8 and 10 as specified in the supplied scheme. These units remain accessible in learning mode. Review-unit excerpts may mix excluded chapters, so this version draws paper evidence from the named eligible units rather than the review pages. Reviews remain available for study.

Paper sections have structural checks, exact quote checks where applicable, and source-ID checks. This does not certify semantic correctness or exact official difficulty. Written answers are for self-review using model answers; there is no automatic subjective grading.

## Update your existing GitHub deployment
1. Keep a copy of the original ZIP.
2. Extract this ZIP.
3. Open the existing GitHub repository and use Add file → Upload files.
4. Upload/replace app.py, core.py, Sections.json, requirements.txt and README.md.
5. Also upload pdf_export.py, units.json, test_app.py and the entire assets folder. Keep assets as a folder; do not flatten its files into the root.
6. Add .streamlit/config.toml from the package if your file manager shows it. If hidden, use GitHub Add file → Create new file; name it .streamlit/config.toml and copy the settings below. The app's main styling works even if this optional theme file is omitted.
7. Commit the changes. Old Extract.py, BuildIndex.py, Retrieve.py and Api.py can remain unused.
8. In Streamlit app settings → Secrets, keep your real key and set:

```toml
GEMINI_API_KEY = "YOUR_EXISTING_REAL_KEY"
GEMINI_MODEL = "PASTE_TESTED_MODEL_ID_HERE"
```

Do not upload the real key to GitHub. The REST generateContent API is used in this version. Model availability and quotas depend on your Google account. There is no guessed default model. Use the temporary model setup panel described in FIXES.md to list candidates and test a JSON response, then save a working model ID in Secrets. The old starter's model setting does not automatically change when you replace the code: edit Secrets explicitly.

9. Main file remains app.py; Python 3.11 or 3.12 is suitable. Reboot the app from Manage app if necessary so dependencies install.
10. Test without being logged into Streamlit, and on a phone.

Optional theme file:
```toml
[theme]
primaryColor = "#127D78"
backgroundColor = "#F6F8F7"
secondaryBackgroundColor = "#EAF0ED"
textColor = "#173B40"
font = "sans serif"
[server]
maxUploadSize = 3
```

## First demonstration
1. Select Unit 3: Daffodils.
2. Open Learn & ask. Choose inferred printed page 32 and explain the page.
3. Select Urdu and repeat, then inspect source text.
4. Open Practice; choose page 32 and generate a five-question check.
5. Complete it. If you miss a concept, use Practise my mistakes for fresh questions.
6. Open My progress and save your progress file.
7. Open Practice paper. Generate each of its nine sections. Quota limits may require spreading requests out. Failed sections can be retried; completed ones remain in the current session.
8. Once all sections are ready, download the paper and separate guide. Do not open the guide until after attempting the paper.

## Local run (optional)
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Create .streamlit/secrets.toml locally with the key settings above; never commit it.

## Test and validation
```bash
python -m unittest test_app.py
```
Offline tests cover book coverage, unit-filtered retrieval, unsupported queries, source-ID rejection, score accuracy, duplicate-submission protection, progress import validation, quote matching, API response parsing and a Streamlit quiz-to-targeted-retry flow with mocked AI responses. PDF English/Urdu layout was checked separately. UI workflows were checked with Streamlit AppTest; desktop/mobile browser screenshot verification was unavailable in this environment.

Live Gemini generation, quota and cloud deployment were not tested with your private account. AI-generated questions, translations and answer keys require review. No real student-impact measurements are claimed. Targeted retry is based on the latest completed quiz, or the latest saved/imported attempt for the selected unit; progress summaries show historical mistakes, not a validated mastery estimate. Changing topics does not silently erase saved attempt history.

## Troubleshooting
- Missing font/file: upload the assets folder and units.json, preserving names and capitalization.
- ModuleNotFoundError: replace requirements.txt and reboot Streamlit.
- 404/model unavailable: change GEMINI_MODEL in Secrets to an available supported model ID.
- 429/quota reached: inspect Google AI Studio usage and retry later. Free hosting does not include unlimited AI calls.
- Invalid source/quote: retry the section. Do not weaken validation just to make a paper export.
- Wrong text/page: verify the OCR with the original PDF; the original is needed for correction.
- Progress disappeared: restore your downloaded JSON. The server session is temporary; papers are also session-only.

## Data and costs
Source files are static; no paid database is required. Questions and selected excerpts go to Google when AI features are used. Keep personal data out of questions. API billing is separate from hosting; session throttling is not a global cost cap. Before a public launch, review your API usage limits and permission to distribute the textbook material. Bundled font licenses are under assets/.
