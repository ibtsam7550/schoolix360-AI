import json
import base64
import os
import time
import uuid
from html import escape
from pathlib import Path
import streamlit as st
from core import (load_data, Search, ai, answer_prompt, validate_answer, quiz_prompt, validate_quiz,
                  grade, record_attempt, import_history, BLUEPRINT, paper_prompt, validate_paper_group)
from pdf_export import export_pdf,paper_pdf

st.set_page_config(page_title='Schoolix360 · Learn your way',page_icon='✦',layout='wide')
st.markdown('''<style>
.block-container{max-width:1180px;padding-top:1.8rem;padding-bottom:2rem}
h1,h2,h3{letter-spacing:-.035em} [data-testid="stSidebar"]{background:#eaf0ed}
.hero{background:linear-gradient(120deg,#102e38,#164d50);padding:32px 36px;border-radius:22px;color:#fff;margin-bottom:24px;position:relative;overflow:hidden}
.hero:after{content:'✦';position:absolute;right:38px;top:-25px;font-size:180px;color:#ffffff0c}
.eyebrow{font-size:11px;letter-spacing:2.2px;text-transform:uppercase;font-weight:700;color:#9cded3}
.hero h1{font-size:38px;color:white;margin:8px 0}.hero p{color:#d0e2e4;max-width:650px;margin-bottom:0;font-size:16px}
.pill{display:inline-block;border:1px solid #ffffff30;border-radius:30px;padding:5px 12px;font-size:12px;margin-top:18px;margin-right:8px;color:#dff7ef}
.card{background:white;border:1px solid #dce5e0;border-radius:16px;padding:22px;height:100%;margin:8px 0 20px}
.card h3{font-size:20px;margin:8px 0}.card p{font-size:14px;color:#52676a}.card .number{color:#127d78;font-size:12px;font-weight:700;letter-spacing:1px}
[data-testid="stMetric"]{background:white;border:1px solid #dce5e0;border-radius:14px;padding:16px}
.stButton>button{border-radius:10px;min-height:42px}.stDownloadButton>button{border-radius:10px}
[data-testid="stExpander"]{background:#fff;border-radius:12px}
.label{color:#68817e;font-size:12px;letter-spacing:1.5px;text-transform:uppercase}
.urdu{direction:rtl;text-align:right;font-family:'Noto Nastaliq Urdu','DejaVu Sans',serif;font-size:20px;line-height:2.1;white-space:pre-wrap;background:white;padding:24px;border-radius:16px;border:1px solid #dce5e0}
@media(max-width:650px){.hero{padding:22px}.hero h1{font-size:28px}.block-container{padding:1rem}.hero:after{display:none}}
</style>''',unsafe_allow_html=True)

@st.cache_data
def urdu_font():
    return base64.b64encode((Path(__file__).parent/'assets/NotoNaskhArabic-Regular.ttf').read_bytes()).decode()
st.markdown("<style>@font-face{font-family:SchoolixUrdu;src:url(data:font/ttf;base64,"+urdu_font()+") format('truetype');}.urdu{font-family:SchoolixUrdu,serif;}</style>",unsafe_allow_html=True)

@st.cache_resource
def resources():
    rows,units=load_data();return rows,units,Search(rows)
rows,units,search=resources();byid={r['id']:r for r in rows}

def setting(name,default=''):
    try:return st.secrets.get(name,os.getenv(name,default))
    except FileNotFoundError:return os.getenv(name,default)
key=setting('GEMINI_API_KEY');model=setting('GEMINI_MODEL','gemini-2.5-flash')
for field,value in [('history',[]),('paper',{}),('nav','Overview')]:
    if field not in st.session_state:st.session_state[field]=value

with st.sidebar:
    st.markdown('### ✦ Schoolix360')
    st.caption('YOUR SPACE TO GROW')
    st.divider()
    selected=st.selectbox('Choose your unit',units,format_func=lambda x:f"{'Unit '+str(x['id']) if x['id']<=11 else 'Review'} · {x['title']}")
    language=st.selectbox('Explain in',['Simple English','Urdu','Roman Urdu'])
    st.caption('Grammar printed inside this English textbook is included. The separate Grammar and Composition book is excluded.')
    st.divider()
    st.markdown('**A little practice. A clearer tomorrow.**')
    st.caption('No student registration. Save a progress file to continue on another day.')
    if not key:st.info('Browse the book now. Add your Gemini key in Secrets to enable AI.')
unit=selected['id'];unit_rows=[r for r in rows if r['unit']==unit]
st.markdown(f'''<div class="hero"><div class="eyebrow">English 9 · Punjab textbook · Student edition</div><h1>Learn your way.<br>Grow with every attempt.</h1><p>Understand a lesson, discover what needs practice, and take your next step with confidence.</p><span class="pill">English + Urdu</span><span class="pill">Textbook sources</span><span class="pill">Practice that responds to you</span></div>''',unsafe_allow_html=True)
nav=st.radio('Your workspace',['Overview','Learn & ask','Practice','My progress','Practice paper'],horizontal=True,key='nav',label_visibility='collapsed')
st.divider()

def call(task,sources):
    if not key:st.error('Add GEMINI_API_KEY in Streamlit Settings → Secrets.');return None
    if time.time()-st.session_state.get('last_call',0)<2:st.info('Please wait a moment before the next request.');return None
    st.session_state.last_call=time.time()
    try:
        with st.spinner('Finding the next step in your learning…'):return ai(key,model,task,sources)
    except ValueError as exc:st.error(str(exc));return None

def source_panel(ids):
    with st.expander('Check the textbook source'):
        st.caption('Printed page = OCR page minus 4, inferred from the contents and unit starts. Original book PDF not provided; page labels and OCR wording are not verified.')
        for sid in ids:
            r=byid[sid];st.markdown(f"**{r['title']} · inferred printed p. {r['page']}**")
            st.caption(f"Source {sid} · OCR page {r['ocr_page']}");st.text(r['text'])

def render_answer(data):
    if language=='Urdu':st.markdown(f'<div class="urdu">{escape(data["answer"])}</div>',unsafe_allow_html=True)
    else:st.markdown(data['answer'])
    if data['unclear']:st.info('The supplied text is unclear or insufficient. Check the original book before relying on this answer.')
    if data['source_ids']:source_panel(data['source_ids'])

if nav=='Overview':
    attempts=st.session_state.history
    cols=st.columns(3)
    for col,metric,value in zip(cols,['Textbook units','Practice attempts','Questions attempted'],[11,len(attempts),sum(a['total'] for a in attempts)]):col.metric(metric,value)
    cols=st.columns(3)
    for col,num,title,desc in zip(cols,['01 / UNDERSTAND','02 / DISCOVER','03 / IMPROVE'],['A lesson that makes sense','Find your learning gaps','Make your next attempt count'],['Ask in English or Urdu. Read an explanation and inspect the source excerpt.','Take a short quiz. See why each answer works and where you need more practice.','Retry the concepts you missed, using fresh questions rather than repeating the same test.']):
        col.markdown(f'<div class="card"><div class="number">{num}</div><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
    st.subheader('Your current chapter')
    st.write(f"**{selected['title']}** · inferred printed pages {selected['start']}–{selected['end']}")
    st.info('Start in Learn & ask, then take a five-question check in Practice. The app uses only the English textbook you supplied.')
    with st.expander('What this edition includes'):
        st.write('All 11 units and both reviews are available for learning. The supplied pairing scheme excludes units 5, 8 and 10 from its paper scope; practice-paper generation follows that exclusion.')
        st.write('Source text is OCR and contains errors. References help you inspect evidence; they do not guarantee an answer is correct. AI scoring of written work is not included; use the model answers for self-review.')

elif nav=='Learn & ask':
    st.subheader(selected['title'])
    page=st.selectbox('Explore a textbook page',list(dict.fromkeys(r['page'] for r in unit_rows)),format_func=lambda p:f'Inferred printed page {p}')
    selected_rows=[r for r in unit_rows if r['page']==page]
    with st.expander('Read the OCR text for this page',expanded=False):
        for r in selected_rows:st.text(r['text'])
    style=st.selectbox('How would you like to learn?',['Explain this page simply','Explain the vocabulary on this page','Help me understand the passage or poem','Explain the textbook exercise on this page'])
    scope=(unit,page,language)
    if st.session_state.get('lesson_scope')!=scope:
        st.session_state.pop('lesson',None);st.session_state.lesson_scope=scope
    if st.button('Explain this page',type='primary',use_container_width=True):
        data=call(answer_prompt(style,language),selected_rows)
        if data is not None:
            try:st.session_state.lesson=validate_answer(data,selected_rows)
            except ValueError as exc:st.error(str(exc))
    with st.form('ask'):
        question=st.text_area('Or ask a question about this chapter',placeholder='What does the poet mean by the inward eye?',max_chars=1000)
        submit=st.form_submit_button('Ask my study companion')
    if submit:
        query=question.strip()
        if not query:st.warning('Write your question first.')
        else:
            if any('\u0600'<=c<='\u06ff' for c in query):
                translated=call('Translate this student question into a short English search query. Return {"query":"..."}. Question: '+query,[])
                query=translated.get('query','') if isinstance(translated,dict) else ''
                # Translation followed by answer is one intentional user action.
                st.session_state.last_call=0
            sources=search.find(query,unit,k=6) if isinstance(query,str) and query else []
            if not sources:st.info('No useful match in this chapter. Try another keyword, a specific page, or another chapter.')
            else:
                data=call(answer_prompt(question,language),sources)
                if data is not None:
                    try:st.session_state.lesson=validate_answer(data,sources)
                    except ValueError as exc:st.error(str(exc))
    if 'lesson' in st.session_state:render_answer(st.session_state.lesson)

elif nav=='Practice':
    st.subheader('Small checks. Meaningful progress.')
    st.caption('Scores use an AI-generated answer key. Review the explanations and cited OCR text if an answer seems wrong.')
    if st.session_state.get('quiz_unit')!=unit:
        st.session_state.pop('quiz',None);st.session_state.pop('responses',None);st.session_state.quiz_unit=unit
    page=st.selectbox('Practice from this page',list(dict.fromkeys(r['page'] for r in unit_rows)),format_func=lambda p:f'Inferred printed page {p}')
    difficulty=st.selectbox('Starting difficulty',['Gentle start','Standard','Challenge'])
    a,b=st.columns(2)
    start=a.button('Start a 5-question check',type='primary',use_container_width=True)
    wrong=[]
    if 'quiz' in st.session_state and 'responses' in st.session_state:
        qz=st.session_state.quiz
        wrong=[dict(q,selected_answer=q['options'][r]) for q,r in zip(qz['items'],st.session_state.responses) if q['answer']!=r]
    if not wrong and 'responses' not in st.session_state:
        previous=[h for h in st.session_state.history if h['unit']==unit]
        if previous:
            wrong=[d for d in previous[-1]['details'] if not d['correct']]
    retry=b.button('Practise my mistakes',disabled=not wrong,use_container_width=True)
    if start or retry:
        sources=[r for r in unit_rows if r['page']==page] if start else [byid[i] for i in dict.fromkeys(s for q in wrong for s in q['source_ids'])]
        data=call(quiz_prompt(5,language,wrong if retry else None,'Gentle start' if retry else difficulty),sources)
        if data is not None:
            try:
                items=validate_quiz(data,5,sources)
                if retry and any(q['question'].strip().lower() in {w['question'].strip().lower() for w in wrong} for q in items):raise ValueError('The AI repeated an old question. Please retry.')
                st.session_state.quiz={'id':uuid.uuid4().hex,'unit':unit,'items':items,'kind':'Targeted retry' if retry else 'Learning check'}
                st.session_state.pop('responses',None)
            except ValueError as exc:st.error(str(exc))
    if 'quiz' in st.session_state:
        qz=st.session_state.quiz
        st.caption(qz['kind'])
        with st.form('q_'+qz['id']):
            responses=[st.radio(f"{i+1}. {q['question']}",list(range(4)),format_func=lambda j,q=q:q['options'][j],index=None,key=qz['id']+str(i),disabled='responses' in st.session_state) for i,q in enumerate(qz['items'])]
            done=st.form_submit_button('Check my understanding',disabled='responses' in st.session_state)
        if done:
            try:
                grade(qz['items'],responses);st.session_state.history=record_attempt(st.session_state.history,qz,responses);st.session_state.responses=responses;st.rerun()
            except ValueError as exc:st.warning(str(exc))
        if 'responses' in st.session_state:
            responses=st.session_state.responses;score=grade(qz['items'],responses)
            st.metric('Your score',f'{score} / 5')
            for i,(q,a) in enumerate(zip(qz['items'],responses),1):
                with st.expander(f"{'✓' if a==q['answer'] else '↻'} {i}. {q['concept']}",expanded=a!=q['answer']):
                    st.write('Your answer: '+q['options'][a]);st.write('Correct answer: '+q['options'][q['answer']]);st.write(q['explanation']);source_panel(q['source_ids'])
            st.info('Next step: use Practise my mistakes above for fresh questions on the concepts you missed.' if score<5 else 'You answered this set correctly. Try another page or a harder set to check your understanding more broadly.')

elif nav=='My progress':
    st.subheader('Your progress belongs to you.')
    st.caption('These records describe quiz attempts, not a certified ability score. No student name or email is required.')
    history=st.session_state.history
    if history:
        st.dataframe([{'Attempt':i+1,'Unit':h['unit'],'Activity':h['kind'],'Score':f"{h['score']}/{h['total']}"} for i,h in enumerate(history)],use_container_width=True,hide_index=True)
        weak={}
        for h in history:
            for d in h['details']:
                if not d['correct']:weak[d['concept']]=weak.get(d['concept'],0)+1
        if weak:
            st.markdown('**Concepts missed across your saved attempts**')
            st.dataframe([{'Concept':k,'Incorrect answers':v} for k,v in sorted(weak.items(),key=lambda x:-x[1])],hide_index=True,use_container_width=True)
        st.download_button('Save my progress (.json)',json.dumps({'version':2,'history':history},ensure_ascii=False),'schoolix-progress.json','application/json')
    else:st.info('Complete your first learning check to see results here.')
    uploaded=st.file_uploader('Restore a saved progress file',type=['json'])
    if st.button('Restore progress',disabled=uploaded is None):
        try:
            if uploaded.size>1_000_000:raise ValueError('Progress file is too large.')
            restored=import_history(json.loads(uploaded.getvalue()),set(byid))
            st.session_state.history=restored;st.success('Progress restored.');st.rerun()
        except (ValueError,KeyError,TypeError) as exc:st.error('Could not restore this progress file. Check that it was exported by this version.')
    if st.checkbox('I want to clear my saved session attempts') and st.button('Clear progress'):
        st.session_state.history=[];st.session_state.pop('responses',None);st.session_state.pop('quiz',None);st.rerun()
    st.caption('Download before leaving. Streamlit session data is temporary; importing a file replaces the current history. Progress files can be edited and are for personal study, not official assessment.')

elif nav=='Practice paper':
    st.subheader('Your textbook-only practice session')
    st.write('**37 marks · Self-study edition · Separate answer guide**')
    st.info('Adapted from the supplied Taleem360 pairing scheme dated 9 April 2026. This is a third-party scheme, not an independently verified board notification. This subset is not a complete 75-mark board paper.')
    with st.expander('See marks and scope',expanded=False):
        st.dataframe([{'Section':s['label'],'Offered':s['n'],'Attempt':s['attempt'],'Marks each':s['marks'],'Total':s['attempt']*s['marks']} for s in BLUEPRINT],hide_index=True,use_container_width=True)
        st.write('Excluded: Q1(A), mixed-source Q1(D), and Q6–Q9 because they draw on the separate Grammar and Composition book. Units 5, 8 and 10 are excluded here by the supplied scheme, but remain available for learning.')
        st.caption('For reliable unit attribution, this version draws paper questions from the named eligible units; review pages are available in learning mode but are not used as paper sources.')
        st.write('No exam duration is set because the supplied scheme does not specify one for this custom subset. Written responses are self-checked using an AI-generated answer guide.')
    st.caption('Build one section at a time to manage API usage. The app preserves completed sections during this session. PDF download becomes available after all sections pass structural checks.')
    spec=st.selectbox('Choose paper section',BLUEPRINT,format_func=lambda s:s['label'])
    if st.button('Generate / replace this section',type='primary'):
        sources=[]
        # Balance evidence across the scheme groups instead of letting one unit dominate.
        for u in spec['units']:
            if u in (12,13):
                continue  # Review OCR mixes excluded chapters; prefer identifiable eligible units.
            candidates=[r for r in rows if r['unit']==u]
            if spec['id']=='translation':
                candidates=[r for r in candidates if r['page'] in {2,3,4,17,18,19,50,51,52,73,74,75,107,108,109}]
            elif spec['id']=='poem':candidates=[r for r in candidates if r['page'] in {32,33,86,87,88,89}]
            elif spec['id']=='play':candidates=search.find('Abel Mrs Slater Jordan possessions grandfather marriage',u,k=7)
            elif 'spell' in spec['id'] or 'meaning' in spec['id'] or spec['id']=='words':
                candidates=search.find('Glossary Words Meanings Vocabulary',u,k=2) or candidates[:2]
            else:candidates=search.find('Reading Critical Thinking Answer questions',u,k=2) or candidates[:2]
            sources.extend(candidates[:7] if spec['id']=='play' else candidates[:3])
        data=call(paper_prompt(spec),sources)
        if data is not None:
            try:st.session_state.paper[spec['id']]=validate_paper_group(data,spec,sources);st.success('Section ready. Choose the next section above.')
            except ValueError as exc:st.error(str(exc))
    paper=st.session_state.paper
    st.progress(len(paper)/len(BLUEPRINT),text=f'{len(paper)} of {len(BLUEPRINT)} sections ready')
    for s in BLUEPRINT:
        if s['id'] in paper:
            with st.expander(s['label']+' · Ready'):
                st.caption(f"Attempt {s['attempt']} of {s['n']}; {s['marks']} mark(s) each")
                for i,q in enumerate(paper[s['id']],1):
                    st.write(f"{i}. {q['question']}")
                    if s['type']=='mcq':
                        for j,o in enumerate(q['options']):st.write(f'{chr(65+j)}. {o}')
    if len(paper)==len(BLUEPRINT):
        a,b=st.columns(2)
        a.download_button('Download question paper PDF',paper_pdf(paper,BLUEPRINT,rows),'schoolix-practice.pdf','application/pdf',use_container_width=True)
        b.download_button('Download answer guide PDF',paper_pdf(paper,BLUEPRINT,rows,True),'schoolix-answer-guide.pdf','application/pdf',use_container_width=True)
        st.caption('Attempt the paper before opening the answer guide. Model answers are AI-generated and should be checked against the textbook.')
    if paper and st.button('Start a fresh paper'):
        st.session_state.paper={};st.rerun()

st.divider()
st.caption('Schoolix360 AI · Learning support, not official grading · Source OCR may contain errors · Questions and selected excerpts are sent to Google when you use AI features')
