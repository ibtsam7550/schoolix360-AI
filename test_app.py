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
 def test_streamlit_quiz_flow(self):
  from streamlit.testing.v1 import AppTest
  with patch.dict(os.environ,{'GEMINI_API_KEY':'fake'}):
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
