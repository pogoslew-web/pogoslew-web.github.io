"""Fusionne les lots traduits (NNN.fr.txt) et génère db/i18n/fr/<type>/<slug>.json pour TOUTES les pages.
Priorité : db/i18n/fr_curated (traductions déjà relues) > gabarits traduits."""
import json,glob,os,re,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fr_lib import *
from fr_rules import auto
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); U=R+'/db/i18n/units'
fr=json.load(open(U+'/fr.json')) if os.path.exists(U+'/fr.json') else {}
bad=0
en=json.load(open(U+'/en_templates.json')) if os.path.exists(U+'/en_templates.json') else {}
for f in sorted(glob.glob(U+'/done/*.fr.txt')+glob.glob(U+'/batches/*.fr.txt')):
    for l in open(f):
        if '|' not in l: continue
        k,v=l.rstrip('\n').split('|',1)
        if k not in en: continue
        if sorted(re.findall(r'⟦\d+⟧',en[k]))!=sorted(re.findall(r'⟦\d+⟧',v)) or sorted(re.findall(r'<(\w+)',en[k]))!=sorted(re.findall(r'<(\w+)',v)):
            bad+=1; print('INCOHÉRENT',k,en[k][:70],'=>',v[:70]); continue
        fr[k]=v
json.dump(fr,open(U+'/fr.json','w'),ensure_ascii=False,indent=0)
print(len(fr),'gabarits traduits,',bad,'rejetés')
LINKS=json.load(open(U+'/links.fr.json')) if os.path.exists(U+'/links.fr.json') else {}
MOIS='janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|janv\\.|févr\\.|avr\\.|juil\\.|sept\\.|oct\\.|nov\\.|déc\\.'
def linkfix(s):
    s=re.sub(r'\b(\d{1,2}), ('+MOIS+r') (\d{4})',r'\1 \2 \3',s)
    return re.sub(r'(<a\b[^>]*>)([^<]*)(</a>)',lambda m:m.group(1)+LINKS.get(m.group(2).strip(),m.group(2))+m.group(3),s)
def tr(inner,title):
    t,vals=templ(inner,title); k=H(t)
    if k in fr: return linkfix(fill(fr[k],vals))
    a=auto(t)
    return linkfix(fill(a,vals)) if a else linkfix(inner)
def block(b,title):
    h=b.get('html','')
    if b['type'] in('ul','ol'): out=re.sub(r'(<li\b[^>]*>)(.*?)(</li>)',lambda m:m.group(1)+tr(m.group(2),title)+m.group(3),h,flags=re.S)
    elif b['type']=='table': out=re.sub(r'(<t[dh]\b[^>]*>)(.*?)(</t[dh]>)',lambda m:m.group(1)+tr(m.group(2),title)+m.group(3),h,flags=re.S)
    elif b['type']=='image': return None
    else: out=tr(h,title)
    return out if out!=h else None
n=0;tot=0;fully=0
for f in sorted(glob.glob(R+'/db/entities/*/*.json')):
    e=json.load(open(f)); t=e['type'];s=e['slug'];title=e['title']
    cur=R+f'/db/i18n/fr_curated/{t}/{s}.json'; c=json.load(open(cur)) if os.path.exists(cur) else {}
    d={'summary':c.get('summary'),'headings':dict(c.get('headings',{})),'blocks':{}}
    if not d['summary'] and e['summary']:
        x=tr(e['summary'],title); d['summary']=x if x!=e['summary'] else None
    secs=[x for x in e['sections'] if x['blocks'] or x['heading']]
    for i,sec in enumerate(secs):
        key=sec.get('id') or f'#{i}'
        if sec.get('heading') and key not in d['headings']:
            x=tr(sec['heading'],title)
            if x!=sec['heading']: d['headings'][key]=x
        cb=c.get('blocks',{}).get(key,{}); bl={}
        for j,b in enumerate(sec['blocks']):
            if str(j) in cb: bl[str(j)]=cb[str(j)]; continue
            x=block(b,title)
            if x: bl[str(j)]=x
        if bl: d['blocks'][key]=bl
    if d['summary'] or d['headings'] or d['blocks']:
        os.makedirs(R+f'/db/i18n/fr/{t}',exist_ok=True); json.dump(d,open(R+f'/db/i18n/fr/{t}/{s}.json','w'),ensure_ascii=False); n+=1
print(n,'pages avec contenu FR')
