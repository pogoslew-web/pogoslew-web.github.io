"""Découpage en fragments + gabarits (nombres, liens, titre -> ⟦n⟧) pour la traduction par lots."""
import re,hashlib
NUM=r'\d[\d,]*(?:\.\d+)?'
TOK=re.compile(r'(<a\b[^>]*>.*?</a>|'+NUM+')',re.S)
WORD=re.compile(r'[A-Za-z]{3,}')
H=lambda s: hashlib.sha1(s.encode()).hexdigest()[:10]
def math_spans(frag):
    """intervalles des formules rendues (<span><span><math…</math>…</span>…</span>) : jetons opaques"""
    out=[];i=0
    while True:
        i=frag.find('<span><span><math',i)
        if i<0: break
        d=0;j=i
        for m in re.finditer(r'<span\b|</span>',frag[i:]):
            d+=1 if m.group(0)!='</span>' else -1
            if d==0: j=i+m.end();break
        if j==i: break
        out.append((i,j)); i=j
    return out
def templ(frag,title=''):
    """-> (gabarit, [valeurs]) : liens, nombres, formules et titre de la page deviennent ⟦n⟧"""
    vals=[]
    pat=TOK
    if title and len(title)>3: pat=re.compile('('+re.escape(title)+'|'+TOK.pattern+')',re.S)
    spans=math_spans(frag)
    if not spans:
        def r(m): vals.append(m.group(0)); return f'⟦{len(vals)}⟧'
        return re.sub(r'\s+',' ',pat.sub(r,frag)).strip(),vals
    out=[];pos=0
    def sub(txt):
        def r(m): vals.append(m.group(0)); return f'⟦{len(vals)}⟧'
        return pat.sub(r,txt)
    for a,b in spans:
        out.append(sub(frag[pos:a])); vals.append(frag[a:b]); out.append(f'⟦{len(vals)}⟧'); pos=b
    out.append(sub(frag[pos:]))
    return re.sub(r'\s+',' ',''.join(out)).strip(),vals
def fill(tmpl,vals):
    def r(m):
        i=int(m.group(1))-1
        return vals[i] if 0<=i<len(vals) else m.group(0)
    return re.sub(r'⟦(\d+)⟧',r,tmpl)
def translatable(t):
    s=re.sub(r'⟦\d+⟧|<[^>]+>','',t)
    return bool(WORD.search(s))
def frags(html,btype):
    """liste de fragments (innerHTML) d'un bloc ; None = bloc entier"""
    if btype in('ul','ol'): return re.findall(r'<li\b[^>]*>(.*?)</li>',html,flags=re.S)
    if btype=='table': return re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',html,flags=re.S)
    return [html]
