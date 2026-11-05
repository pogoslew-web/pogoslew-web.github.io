"""Extrait les gabarits uniques à traduire -> db/i18n/units/batches/NNN.en.txt  (lignes « id|gabarit »)
Traductions : db/i18n/units/batches/NNN.fr.txt (mêmes ids) -> fusionnées par fr_apply.py dans db/i18n/units/fr.json"""
import json,glob,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fr_lib import *
from fr_rules import auto
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U=R+'/db/i18n/units'
fr=json.load(open(U+'/fr.json')) if os.path.exists(U+'/fr.json') else {}
need={}
def want(t,kind=''):
    if not translatable(t) or '<math' in t: return
    if re.fullmatch(r'(<img[^>]*>|\s|⟦\d+⟧)*',t) or re.fullmatch(r'<p>(<img[^>]*>)</p>',t): return
    plain=re.sub(r'<[^>]+>|⟦\d+⟧','',t).strip()
    if kind=='td' and '<a' not in t and re.fullmatch(r"(?:[A-Z][\w'’.&-]*\s?){2,4}",plain): return  # nom propre en tableau
    need[H(t)]=t
def scan(frag,title,kind):
    t,_=templ(frag,title); want(t,kind)
for f in sorted(glob.glob(R+'/db/entities/*/*.json')):
    e=json.load(open(f)); title=e['title']
    if e['summary']: scan(e['summary'],title,'s')
    for s in e['sections']:
        if s.get('heading'): scan(s['heading'],title,'h')
        for b in s['blocks']:
            if b['type']=='image': continue
            for fr_ in frags(b.get('html',''),b['type']): scan(fr_,title,'td' if b['type']=='table' else 'b')
json.dump(need,open(U+'/en_templates.json','w'),ensure_ascii=False)
todo={k:v for k,v in need.items() if k not in fr and not auto(v)}
print(len(need),'gabarits,',len(todo),'à traduire,',sum(len(v) for v in todo.values()),'car.')
os.makedirs(U+'/batches',exist_ok=True)
for f in glob.glob(U+'/batches/*.en.txt'): os.remove(f)
items=sorted(todo.items(),key=lambda kv:re.sub(r'<[^>]+>|⟦\d+⟧','',kv[1])[:25].lower())
n=0;size=0;buf=[]
def dump():
    global n,size,buf
    open(f'{U}/batches/{n:03d}.en.txt','w').write(''.join(f'{k}|{v}\n' for k,v in buf)); n+=1;size=0;buf=[]
for k,v in items:
    buf.append((k,v)); size+=len(v)+14
    if size>16000: dump()
if buf: dump()
print(n,'lots')
