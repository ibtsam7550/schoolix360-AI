"""PDF exports with bundled fonts and shaped Urdu lines."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import re
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).parent
pdfmetrics.registerFont(TTFont('Urdu',str(ROOT/'assets/NotoNaskhArabic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Schoolix',str(ROOT/'assets/DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('SchoolixBold',str(ROOT/'assets/DejaVuSans-Bold.ttf')))

def export_pdf(title,blocks):
    stream=BytesIO(); c=canvas.Canvas(stream,pagesize=(595,842)); c.setTitle(title)
    y=0; page=0
    def new_page():
        nonlocal y,page
        if page:c.showPage()
        page+=1
        c.setFillColorRGB(.055,.14,.18);c.rect(0,774,595,68,fill=1,stroke=0)
        c.setFillColorRGB(1,1,1);c.setFont('SchoolixBold',18);c.drawString(42,806,'SCHOOLIX360 AI')
        c.setFont('Schoolix',9);c.drawString(42,789,'ENGLISH 9  /  INDEPENDENT LEARNING')
        c.setFillColorRGB(.3,.36,.4);c.setFont('Schoolix',8);c.drawString(42,24,'Textbook-only practice | AI-generated; check source text')
        c.drawRightString(552,24,str(page));y=752
    new_page()
    for text,bold in [(title,True)]+blocks:
        text=str(text).replace('\x00','')
        size=12 if bold else 10
        font='SchoolixBold' if bold else 'Schoolix'
        for para in text.split('\n'):
            is_urdu=bool(re.search(r'[\u0600-\u06ff]',para))
            para_font='Urdu' if is_urdu else font
            para_size=13 if is_urdu else size
            lines=simpleSplit(para,para_font,para_size,500) or ['']
            for line in lines:
                if y<58:new_page()
                c.setFont(para_font,para_size);c.setFillColorRGB(.07,.16,.2)
                if re.search(r'[\u0600-\u06ff]',line):
                    shaped=get_display(arabic_reshaper.reshape(line));c.drawRightString(551,y,shaped)
                else:c.drawString(42,y,line)
                y-=23 if is_urdu else (17 if bold else 15)
        y-=8
    c.save();return stream.getvalue()

def paper_pdf(paper,blueprint,rows,answers=False):
    lookup={r['id']:r for r in rows}; blocks=[('37 marks | Textbook-only subset of the supplied 2026 scheme.',False),('This is not a complete board examination paper. No separate Grammar and Composition book content is included. Printed pages are inferred from OCR and remain unverified.',False)]
    for spec in blueprint:
        blocks.append((spec['label'],True));blocks.append((f"Attempt {spec['attempt']} out of {spec['n']}. {spec['marks']} mark(s) each. Section total: {spec['attempt']*spec['marks']}.",False))
        for i,q in enumerate(paper[spec['id']],1):
            blocks.append((f"{i}. {q['question']}",False))
            if not answers:
                if spec['type']=='mcq':blocks.extend((f"   {chr(65+j)}. {o}",False) for j,o in enumerate(q['options']))
                else:blocks.append(('Answer: __________________________________________________________',False))
            else:
                ans=q['options'][q['answer']] if spec['type']=='mcq' else q['answer']
                blocks.extend([(f'Answer: {ans}',False),(f"Guidance: {q['explanation']}",False)])
                refs=', '.join(f"{sid} (inferred p. {lookup[sid]['page']})" for sid in q['source_ids'])
                blocks.append((f'Sources: {refs}',False))
    return export_pdf('Practice answer guide' if answers else 'My English practice paper',blocks)
