import os
import time
import uuid
import requests
import streamlit as st
from core import load_sections, retrieve, generate, assessment_prompt, parse_questions, export_test

st.set_page_config(page_title='Schoolix360 AI | English', page_icon='📚', layout='wide')
st.title('📚 Schoolix360 AI')
st.write('Grade 9 English • Learn, practise, and build confidence')
st.caption('Prototype based on supplied study notes. Content and page references have not been checked against the original English PDF.')

@st.cache_data
def notes():
    return load_sections()

def setting(name, default=''):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except FileNotFoundError:
        return os.getenv(name, default)

key = setting('GEMINI_API_KEY')
model = setting('GEMINI_MODEL', 'gemini-3.8-flash')
all_notes = notes()
with st.sidebar:
    st.header('Your classroom')
    unit = st.selectbox('Unit', list(dict.fromkeys(s['unit'] for s in all_notes)))
    language = st.selectbox('Explanation language', ['English', 'Urdu', 'Roman Urdu'])
    st.caption('Ask search questions using English keywords. Explanations can be in any language above.')
    st.caption('No account needed. Quizzes and results last for this session only.')
    if st.button('Clear session work'):
        for field in ['quiz', 'result', 'test', 'reply', 'last_request']:
            st.session_state.pop(field, None)
        st.rerun()
selected = [s for s in all_notes if s['unit'] == unit]
topic = st.selectbox('Topic', [s['topic'] for s in selected])
section = next(s for s in selected if s['topic'] == topic)
scope = (unit, topic, language)
if st.session_state.get('scope') != scope:
    for field in ['quiz', 'result', 'test', 'reply']:
        st.session_state.pop(field, None)
    st.session_state.scope = scope

def call(task, sources):
    if not key:
        st.error('Add GEMINI_API_KEY in Streamlit app settings → Secrets, then restart the app.')
        return None
    if time.time() - st.session_state.get('last_request', 0) < 4:
        st.info('Please wait a few seconds before another AI request.')
        return None
    st.session_state.last_request = time.time()
    try:
        with st.spinner('Preparing your learning material…'):
            return generate(key, model, task, sources)
    except RuntimeError as exc:
        st.error(str(exc))
        return None
    except (requests.RequestException, ValueError):
        # Do not print raw HTTP request exceptions, which may contain credentials.
        st.error('The AI request could not finish. Check model access, the API key, and quota in Google AI Studio. If quota is exhausted, retry later. Check Streamlit Secrets for the exact model ID.')
        return None

def show_sources(sources):
    with st.expander('Study notes used and supplied page references'):
        for s in sources:
            st.markdown(f"**[{s['id']}] {s['topic']}**")
            st.caption(f"{s['unit']} | Supplied printed page: {s['printedPage']} | Supplied PDF page: {s['pdfPage']} (unverified)")
            st.write(s['text'])

learn, quiz, test = st.tabs(['Learn & Ask', 'Quiz Practice', 'Create a Test'])
with learn:
    st.subheader(topic)
    if st.button('Teach me this topic', type='primary'):
        answer = call(f'Explain this topic simply in {language}. Include one vocabulary word with its meaning.', [section])
        if answer:
            st.session_state.reply = (answer, [section])
    with st.form('ask'):
        question = st.text_input('Ask about this unit using English keywords', placeholder='What is a gerund?', max_chars=700)
        ask = st.form_submit_button('Ask the tutor')
    if ask:
        if not question.strip():
            st.warning('Please enter a question.')
        else:
            sources = retrieve(question, selected)
            if not sources:
                st.session_state.reply = ('I could not find relevant notes in this unit. Try English keywords or select another unit.', [])
            else:
                answer = call(f'Answer in {language}. Student question: {question}', sources)
                if answer:
                    st.session_state.reply = (answer, sources)
    if 'reply' in st.session_state:
        answer, sources = st.session_state.reply
        st.markdown(answer)
        show_sources(sources)
    else:
        show_sources([section])

with quiz:
    st.subheader('Five questions. One step forward.')
    if st.button('Generate 5-question quiz'):
        raw = call(assessment_prompt(5, language), [section])
        if raw:
            try:
                items = parse_questions(raw, 5)
                st.session_state.quiz = {'id': uuid.uuid4().hex, 'items': items}
                st.session_state.pop('result', None)
            except (ValueError, KeyError, TypeError):
                st.error('The AI returned an invalid quiz format. Please generate again.')
    if 'quiz' in st.session_state:
        data = st.session_state.quiz
        with st.form('quiz_' + data['id']):
            responses = [st.radio(f"{i+1}. {q['question']}", range(4),
                         format_func=lambda j, q=q: q['options'][j], index=None,
                         key=f"{data['id']}_{i}") for i, q in enumerate(data['items'])]
            submitted = st.form_submit_button('Submit answers')
        if submitted:
            if any(x is None for x in responses):
                st.warning('Answer all five questions before submitting.')
            else:
                st.session_state.result = responses
        if 'result' in st.session_state:
            responses = st.session_state.result
            score = sum(a == q['answer'] for a, q in zip(responses, data['items']))
            st.metric('Your score', f'{score}/5')
            for i, (a, q) in enumerate(zip(responses, data['items']), 1):
                st.write(f"{i}. {'Correct' if a == q['answer'] else 'Revise this'} — {q['options'][q['answer']]}")
                st.write(q['explanation'])
            if score < 5:
                st.info('Return to Learn & Ask to revise this topic, then try a new quiz.')

with test:
    st.subheader('Download an MCQ practice test')
    st.write('The test covers the selected topic. Each question carries one mark.')
    count = st.selectbox('Questions / total marks', [5, 10])
    if st.button('Generate practice test'):
        raw = call(assessment_prompt(count, language), [section])
        if raw:
            try:
                items = parse_questions(raw, count)
                title = f'Schoolix360 AI - Grade 9 English\n{unit}\n{topic}'
                st.session_state.test = export_test(items, title)
            except (ValueError, KeyError, TypeError):
                st.error('The AI returned an invalid test format. Please generate again.')
    if 'test' in st.session_state:
        paper, answer_key = st.session_state.test
        st.text(paper)
        st.download_button('Download question paper (.txt)', paper.encode('utf-8'), 'schoolix360-test.txt', 'text/plain')
        st.download_button('Download separate answer key (.txt)', answer_key.encode('utf-8'), 'schoolix360-answers.txt', 'text/plain')
        st.caption('Open the text file in Word or Google Docs to format and export it as PDF.')

st.divider()
st.caption('AI-generated learning support • Review important answers with your teacher • No official board endorsement')
