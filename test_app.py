"""Offline checks. Run: python -m unittest test_app.py"""
import copy,json,os,unittest
from unittest.mock import patch
from core import *

class CoreTests(unittest.TestCase):
 def setUp(self):self.rows,self.units=load_data();self.source=self.rows[:1]
 def fixture(self):return [{'question':f'Example {i}?','options':['a','b','c','d'],'answer':0,'concept':'Meaning','explanation':'Because a matches the source.','source_ids':[self.source[0]['id']]} for i in range(5)]
 def test_book_and_scheme(self):
  self.assertEqual(len({r['page'] for r in self.rows}),164)
  self.assertEqual(len({r['unit'] for r in self.rows}),13)
  self.assertEqual(sum(s['attempt']*s['marks'] for s in BLUEPRINT),37)
  self.assertTrue(all(not set(s['units']) & {5,8,10} for s in BLUEPRINT))
 def test_retrieval_scope(self):
  r=Search(self.rows).find('gerund infinitive',2)
  self.assertTrue(r);self.assertTrue(all(x['unit']==2 for x in r))
  self.assertEqual(Search(self.rows).find('zzzzxxxxxxxx999999'),[])
 def test_reject_invalid_citation(self):
  q=self.fixture();q[0]['source_ids']=['invented']
  with self.assertRaises(ValueError):validate_quiz({'questions':q},5,self.source)
 def test_scoring_and_import(self):
  q={'id':'test','unit':1,'kind':'Learning check','items':self.fixture()}
  h=record_attempt([],q,[0,1,0,1,0]);self.assertEqual(h[0]['score'],3)
  self.assertEqual(len(record_attempt(h,q,[0]*5)),1)
  self.assertEqual(import_history({'version':2,'history':h},{r['id'] for r in self.rows}),h)
  bad=copy.deepcopy(h);bad[0]['score']=5
  with self.assertRaises(ValueError):import_history({'version':2,'history':bad},{r['id'] for r in self.rows})
 def test_exact_quote(self):
  spec={'id':'custom','n':1,'type':'written'}
  q={'question':'Explain fabricated quote','answer':'answer','explanation':'guide','source_ids':[self.source[0]['id']],'source_text':'fabricated quote'}
  with self.assertRaises(ValueError):validate_paper_group({'questions':[q]},spec,self.source)
 def test_api_secret_not_in_url_and_json(self):
  with patch('core.requests.post') as post:
   post.return_value.status_code=200
   post.return_value.json.return_value={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'{"answer":"hello"}'}]}}]}
   self.assertEqual(ai('SECRET','gemini-2.5-flash','task',self.source),{'answer':'hello'})
   self.assertNotIn('SECRET',post.call_args.args[0])
 def test_list_pagination_filter_and_header(self):
  with patch('core.requests.get') as get:
   first=unittest.mock.Mock(status_code=200)
   first.json.return_value={'models':[{'name':'models/gemini-example','supportedGenerationMethods':['generateContent']},{'name':'models/gemini-image','supportedGenerationMethods':['generateContent']}],'nextPageToken':'next'}
   second=unittest.mock.Mock(status_code=200)
   second.json.return_value={'models':[{'name':'models/gemini-other','supportedGenerationMethods':['generateContent']},{'name':'models/embed','supportedGenerationMethods':['embedContent']}]}
   get.side_effect=[first,second]
   self.assertEqual(list_text_models('SECRET'),['gemini-example','gemini-other'])
   self.assertEqual(get.call_args.kwargs['params']['pageToken'],'next')
   self.assertEqual(get.call_args.kwargs['headers']['x-goog-api-key'],'SECRET')
   self.assertNotIn('SECRET',get.call_args.args[0])
 def test_setup_panel(self):
  from streamlit.testing.v1 import AppTest
  with patch.dict(os.environ,{'GEMINI_API_KEY':'fake','ENABLE_MODEL_SETUP':'true','GEMINI_MODEL':''}):
   at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
   with patch('core.list_text_models',return_value=['gemini-example']):
    next(b for b in at.button if b.label=='Load available Gemini models').click().run()
    self.assertFalse(at.exception)
   with patch('core.ai',return_value={'ok':True}):
    next(b for b in at.button if b.label=='Test selected model').click().run()
    self.assertFalse(at.exception)
    self.assertEqual(at.session_state['tested_model'],'gemini-example')
    self.assertTrue(any('GEMINI_MODEL' in c.value for c in at.code))
 def test_theme_has_no_fixed_light_surfaces(self):
  source=(ROOT/'app.py').read_text()
  self.assertNotIn('background:white',source)
  self.assertNotIn('background:#fff;',source)
  self.assertIn('color:inherit!important',source)
 def test_streamlit_quiz_flow(self):
  from streamlit.testing.v1 import AppTest
  with patch.dict(os.environ,{'GEMINI_API_KEY':'fake','GEMINI_MODEL':'test-model'}):
   at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
   self.assertFalse(at.exception)
   for nav in ['Learn & ask','My progress','Practice paper','Practice']:
    at.radio[0].set_value(nav).run();self.assertFalse(at.exception)
   with patch('core.ai',return_value={'questions':self.fixture()}):
    next(b for b in at.button if b.label=='Start a 5-question check').click().run()
    self.assertFalse(at.exception)
    for r in at.radio[1:]:r.set_value(1)
    next(b for b in at.button if b.label=='Check my understanding').click().run()
    self.assertFalse(at.exception)
    self.assertEqual(at.session_state['history'][0]['score'],0)
    self.assertFalse(next(b for b in at.button if b.label=='Practise my mistakes').disabled)
    newer=self.fixture()
    for q in newer:q['question']='Retry '+q['question']
    at.session_state['last_call']=0
    with patch('core.ai',return_value={'questions':newer}):
     next(b for b in at.button if b.label=='Practise my mistakes').click().run()
     self.assertFalse(at.exception)
     self.assertEqual(at.session_state['quiz']['kind'],'Targeted retry')

if __name__=='__main__':unittest.main()
