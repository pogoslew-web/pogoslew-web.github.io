"""Reconstruit les fiches des 8 classes secrètes sur le modèle de la fiche Assassin.
Sources UNIQUEMENT : cartes de classe (overlay), fiche d'origine du wiki, fiches compétences / passifs de la base. Rien d'inventé."""
import json,glob,re,html as H,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J=lambda p:json.load(open(R+'/'+p))
cards=J('db/overlays/class_cards.json')['classes']
esc=lambda s:H.escape(s,quote=False)
def p(h): return {'type':'p','text':re.sub(r'<[^>]+>','',h),'html':f'<p>{h}</p>'}
def table(headers,rows):  # rows : liste de listes de (text,href|None)
    th=''.join(f'<th>{esc(h)}</th>' for h in headers)
    tr=''.join('<tr>'+''.join(f'<td>{("<a href=%s>%s</a>"%(chr(34)+c[1]+chr(34),esc(c[0]))) if c[1] else esc(c[0])}</td>' for c in r)+'</tr>' for r in rows)
    return {'type':'table','headers':headers,'rows':[[{'text':c[0],**({'href':c[1]} if c[1] else {})} for c in r] for r in rows],'html':f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'}
def ul(items): return {'type':'ul','items':[re.sub(r'<[^>]+>','',i) for i in items],'html':'<ul>'+''.join(f'<li>{i}</li>' for i in items)+'</ul>'}
skills=[];passives=[]
for f in sorted(glob.glob(R+'/db/entities/skills/*.json')):
    x=json.load(open(f)); skills.append((x['slug'],x['title'],{i['key']:i['value'] for i in x['infobox']}))
for f in sorted(glob.glob(R+'/db/entities/passives/*.json')):
    x=json.load(open(f)); passives.append((x['slug'],x['title'],{i['key']:i['value'] for i in x['infobox']}))
out={}
for slug,c in cards.items():
    e=J(f'db/entities/classes/{slug}.json'); title=e['title']
    sec={s['id']:s for s in e['sections'] if s.get('id')}
    wk=''.join((b.get('html') or '') for b in sec.get('what-we-know',{'blocks':[]})['blocks'])
    win=re.search(r'described as:\s*(?:<[^>]+>)*\s*([^<]+?)\s*(?:<|\.)',wk); whisper=re.search(r'whispers:\s*(?:<[^>]+>)*\s*([^<]+?)\s*<',wk)
    tbl={}
    for b in sec.get('stats-and-skills',{'blocks':[]})['blocks']:
        for r in b.get('rows',[]):
            if len(r)==2: tbl[r[0]['text']]=r[1]['text']
    S=[]
    ov=[p(esc(c['desc']))]
    if win: ov.append(p(f'In the class window it is described as: <em>{esc(win.group(1))}</em>.'))
    if whisper: ov.append(p(f'The game whispers: <em>{esc(whisper.group(1).strip())}</em>'))
    ov.append(p('It is one of the <strong>special classes</strong>: they cannot be picked freely, you have to earn them.'))
    S.append({'id':'overview','heading':'Overview','blocks':ov})
    if 'playstyle' in sec: S.append(sec['playstyle'])
    rows=[]
    for b in c['on']:
        m=re.match(r'^(Up to )?([+-]\d+%)\s+(.+)$',b)
        rows.append([((m.group(3)[0].upper()+m.group(3)[1:]),None),(((m.group(1) or '')+m.group(2)),None)] if m else [(b,None),('',None)])
    S.append({'id':'bonuses','heading':'Bonuses','blocks':[table(['Bonus','Value'],rows),p('<strong>Weapons and armor:</strong> '+esc(c['rule']))]})
    eq=[]
    if c['weapons']: eq.append('<strong>Weapons:</strong> '+esc(', '.join(c['weapons'])))
    if c['armor']: eq.append('<strong>Armor:</strong> '+esc(', '.join(c['armor'])))
    eq.append('<strong>Stats to focus:</strong> '+esc(', '.join(c['stats'])))
    eq.append('<strong>Level cap:</strong> 999')
    S.append({'id':'equipment','heading':'Equipment','blocks':[ul(eq)]})
    mine=[s for s in skills if s[2].get('Class')==title]
    sk=[]
    if mine:
        sk.append(p(f'Skills of the {esc(title)} tree. Spend skill points to unlock and level them; each level past the first adds 15% power and removes 5% of the cooldown.'))
        sk.append(table(['Skill','Element','Cooldown','Damage'],[[(t,f'/en/w/overrank/skills/{sl}'),(d.get('Element','-'),None),(d.get('Cooldown','-'),None),(d.get('Damage','-'),None)] for sl,t,d in mine]))
    else:
        sk.append(p('It has no skill tree of its own: it uses the General tree, open to every class.'))
    sk.append(p('<strong>Skill trees:</strong> '+esc(', '.join(c['trees']))+'.'))
    S.append({'id':'skills','heading':'Skills','blocks':sk})
    ptree={'bipolar':'Duality'}.get(slug,title)
    pas=[q for q in passives if q[2].get('Tree')==ptree]
    if pas:
        S.append({'id':'passives','heading':'Passives','blocks':[ul([f'<a href="/en/w/overrank/passives/{sl}">{esc(t)}</a>: {esc(d["Per level"])} per level (up to {esc(d["At max"])})' for sl,t,d in pas if 'Per level' in d])]})
    un=[p(esc(c['unlock'])+' (community-reported)')]
    orig=''.join((b.get('text') or '') for b in sec.get('how-to-unlock',{'blocks':[]})['blocks'])
    if orig and not orig.startswith('Some say') and orig.strip().lower()!=c['unlock'].strip().lower(): un.insert(0,p(esc(orig)))
    un.append(p('Unlock conditions come from the community and have not been verified by the original wiki.'))
    S.append({'id':'how-to-unlock','heading':'How to unlock','blocks':un})
    for k in ('class-card','gear'):
        if k in sec: S.append(sec[k])
    out[slug]={'sections':S,'infobox_fill':{k:tbl[k] for k in ('Role','Difficulty') if tbl.get(k) not in (None,'???')},'incomplete_at_source':False}
json.dump(out,open(R+'/db/overlays/class_pages.json','w'),ensure_ascii=False,indent=1)
print({k:[s['id'] for s in v['sections']] for k,v in out.items()})
