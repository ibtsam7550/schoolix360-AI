# Fix dark mode and Gemini model selection

## Install on your existing v2 app
1. Extract this ZIP.
2. In GitHub, replace app.py AND core.py together with the files from this ZIP. The other files in this full package are supplied for convenience; no data migration is required.
3. Commit changes and reboot Streamlit from Manage app.
4. Open Streamlit Settings > Secrets. Keep your existing GEMINI_API_KEY private. Temporarily add:

```toml
ENABLE_MODEL_SETUP = true
```

You may leave the old GEMINI_MODEL value until the test succeeds. Model setup does not rely on that value.

5. Save. Open the app sidebar (on a phone, tap the sidebar arrow near the upper-left).
6. Expand AI connection setup. Click Load available Gemini models.
7. Choose a candidate from the actual list, then click Test selected model. This makes one small generation request using JSON, as required by the app. Listing itself does not generate a lesson.
8. On success, the app displays two settings. Copy them into Streamlit Secrets, replacing the old GEMINI_MODEL line and changing ENABLE_MODEL_SETUP to false. Keep GEMINI_API_KEY unchanged. For example, use the EXACT ID from your successful test, not the placeholder below:

```toml
GEMINI_MODEL = "EXACT_ID_FROM_THE_SUCCESSFUL_TEST"
ENABLE_MODEL_SETUP = false
```

9. Save and reboot. Try a short lesson, then a quiz.
10. Switch Streamlit Settings > Theme between light and dark to check visibility. As a temporary workaround before uploading the fix, select Light.

## Why this fixes the display
The old CSS forced white backgrounds on custom cards and native metric panels. Dark mode changed inherited text to white, making headings and numbers disappear. Fixed light backgrounds were also applied to the sidebar, expander and Urdu panel. The updated CSS lets those surfaces and text inherit Streamlit's theme. The intentionally dark hero keeps explicit high-contrast light text.

## What the model setup does and does not establish
Uses Google's models.list endpoint with your key in a request header, handles pagination, and filters for Gemini generateContent candidates while excluding obvious image/audio/live models. The catalogue can advertise models that your account cannot currently generate with. A successful small JSON test verifies that request at that time; it does not guarantee free-tier availability, unlimited quota, sufficient limits for full papers, or factual accuracy.

There is no automatic fallback to a different model, because that could change usage costs. There is no hardcoded model default in this version. Student work uses the configured GEMINI_MODEL after you save it; selecting or testing a candidate alone does not change the saved deployment configuration.

This temporary setup panel is visible to anyone who can access the app while ENABLE_MODEL_SETUP is true. It never reveals the key. Turn it off after setup to avoid leaving model-test buttons in the student interface.

## If a request still fails
- 400: invalid API key, request setting, or unsupported JSON configuration may be involved; check the key/project or another compatible candidate.
- 403: check key restrictions and API/project permissions.
- 404: the configured model may be unavailable on the API endpoint; list candidates again.
- 429: rate limit or quota exhaustion; this does not mean the model has been removed. Check Google AI Studio usage and retry when quota is available.
- Listing success but JSON test failure: choose another candidate or resolve the reported permissions/quota issue.

Do not share the key. Share the displayed error text if you need help diagnosing it.

## Validation
Automated tests use mocked API responses for model-list pagination/filtering, header-only credentials, model-test UI, and quiz/retry flows. No real key was used, so a live account check remains necessary. CSS checks confirm the removed fixed white surfaces; the supplied screenshots established the original contrast failure. This turn did not perform a live browser screenshot comparison.

Official reference: https://ai.google.dev/api/models
