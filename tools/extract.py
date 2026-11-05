import re, json, sys, os, html as H
from bs4 import BeautifulSoup, NavigableString
RAW="/home/claude/overrank/raw"
inv=json.load(open(RAW+"/inventory.json"))
KEEP={"href","src","alt","colspan","rowspan","data-toc"}
def clean(el):
    el=BeautifulSoup(str(el),"lxml").body
    for sv in el.find_all("svg"):
        if sv.get("aria-label")=="Affected by luck":
            sp=BeautifulSoup('<span role="img" aria-label="Affected by luck" title="Affected by luck" class="luck">\u2726</span>',"lxml").span; sv.replace_with(sp)
    for s in el.find_all(["svg","script","style","button"]): s.decompose()
    for t in el.find_all(True):
        t.attrs={k:v for k,v in t.attrs.items() if k in KEEP}
    for t in el.find_all(["span","div"]):
        if t.name=="span" and t.get("class") is None and not t.attrs: pass
    inner="".join(str(c) for c in el.children)
    return re.sub(r"\s+"," ",inner).strip()
def text(el): return re.sub(r"\s+"," ",el.get_text(" ",strip=True)).strip()
def table(t):
    heads=[text(th) for th in t.find_all("th")] if t.find("thead") else []
    rows=[]
    for tr in (t.find("tbody") or t).find_all("tr"):
        cells=[]
        for td in tr.find_all(["td","th"]):
            a=td.find("a"); im=td.find("img")
            c={"text":text(td)}
            if a and a.get("href"): c["href"]=a["href"]
            if im and im.get("src"): c["img"]=im["src"]
            cells.append(c)
        if cells: rows.append(cells)
    return {"headers":heads,"rows":rows}
def blocks_of(node):
    out=[]
    for ch in node.children:
        if isinstance(ch,NavigableString):
            continue
        n=ch.name
        if n in("h3","h4"):
            out.append({"type":"heading","level":int(n[1]),"id":ch.get("id"),"text":text(ch)})
        elif n=="table":
            out.append({"type":"table",**table(ch),"html":clean(ch)})
        elif n in("p","ul","ol","blockquote","pre","dl","details"):
            out.append({"type":n,"text":text(ch),"html":clean(ch)})
        elif n=="div" or n=="section" or n=="figure":
            if ch.find("table") and not ch.find(["p","ul","ol","h3"]):
                for t in ch.find_all("table"): out.append({"type":"table",**table(t),"html":clean(t)})
            elif ch.find(["p","ul","ol","h3","h4","table","details","dl"]):
                out.extend(blocks_of(ch))
            elif ch.find("img") or ch.find("model-viewer"):
                out.append({"type":"media","text":text(ch),"html":clean(ch)})
            elif text(ch):
                out.append({"type":"div","text":text(ch),"html":clean(ch)})
        elif n=="model-viewer":
            out.append({"type":"model","src":ch.get("src"),"alt":ch.get("alt")})
        elif n=="img":
            out.append({"type":"image","src":ch.get("src"),"alt":ch.get("alt")})
        elif text(ch):
            out.append({"type":n,"text":text(ch),"html":clean(ch)})
    return out
pages=[]
for url,v in sorted(inv.items()):
    if v["status"]!=200: continue
    s=BeautifulSoup(open(v["file"],encoding="utf-8").read(),"lxml")
    art=s.find("article")
    P={"url":"https://overrank.awaitlab.com"+url,"path":url,"title_tag":s.title.get_text() if s.title else None}
    md=s.find("meta",attrs={"name":"description"}); P["meta_description"]=md["content"] if md else None
    if not art: P["error"]="no article"; pages.append(P); continue
    h1=art.find("h1"); P["title"]=text(h1) if h1 else None
    hdr=art.find("header")
    if hdr:
        p=h1.find_next_sibling("p") if h1 else None
        P["subtitle"]=text(p) if p else None
        bc=hdr.find("nav",attrs={"aria-label":"Breadcrumb"})
        P["breadcrumb"]=[{"text":text(a),"href":a.get("href")} for a in bc.find_all(["a","span"]) ] if bc else []
        m=re.search(r"Last edited by (.*?) · (.*?)$",text(hdr))
        if m: P["last_edited_by"],P["last_edited"]=m.group(1),m.group(2)[:20].strip()
    # quick facts (first group)
    qf=art.find(attrs={"aria-label":"Quick facts"})
    if qf:
        P["infobox"]=[{"key":text(d.find("dt")),"value":text(d.find("dd")),"html":clean(d.find("dd"))} for d in qf.parent.find_all("div",recursive=True) if d.find("dt",recursive=False) and d.find("dd",recursive=False)]
        im=qf.find("img"); P["image"]={"src":im["src"],"alt":im.get("alt")} if im else None
    # main body
    first=None
    for h2 in art.find_all("h2"):
        if h2.get("id"): first=h2; break
    body=[]
    if first:
        cont=first.parent
        cur=None
        for b in blocks_of(cont):
            pass
        # sectionize
        secs=[]; cur={"id":None,"heading":None,"blocks":[]}
        for ch in cont.children:
            if isinstance(ch,NavigableString): continue
            if ch.name=="h2":
                if cur["blocks"] or cur["heading"]: secs.append(cur)
                cur={"id":ch.get("id"),"heading":text(ch),"blocks":[]}
            else:
                cur["blocks"].extend(blocks_of(BeautifulSoup(f"<div>{ch}</div>","lxml").div) if ch.name in("div","section") else blocks_of(BeautifulSoup(f"<div>{ch}</div>","lxml").div))
        if cur["blocks"] or cur["heading"]: secs.append(cur)
        P["sections"]=secs
        # siblings after content div inside article: 3D model etc.
        extra=[]
        for sib in cont.find_next_siblings():
            mv=sib.find("model-viewer") if sib.name!="model-viewer" else sib
            if mv: extra.append({"type":"model","src":mv.get("src"),"alt":mv.get("alt")})
        P["extra_media"]=extra
    elif url=="/en/w/overrank/odds":
        main=s.find("main"); arts=main.find_all("article"); root=arts[0].parent.parent
        kids=[c for c in root.children if getattr(c,"name",None)]
        first=kids[0]; secs=[]
        groups=[text(b) for b in first.find_all("button") if text(b)]
        mods=[]
        for lab in first.find("details").find_all("label"):
            sel=lab.find("select")
            if sel: mods.append("%s: %s"%(text(lab.find("span")),", ".join(text(o) for o in sel.find_all("option"))))
            else: mods.append(re.sub(r"\s+"," ",text(lab)).replace("+ ","+"))
        secs.append({"id":"luck-modifiers","heading":"Luck modifiers","blocks":[
            {"type":"p","text":"Luck bonuses available on the original calculator (default: none selected; attempts = 100).","html":"<p>Luck bonuses available on the original calculator (default: none selected; attempts = 100).</p>"},
            {"type":"ul","text":" ".join(mods),"html":"<ul>"+"".join("<li>%s</li>"%m for m in mods)+"</ul>"}]})
        for a in arts:
            h=a.find("h2"); hdr=a.find("header"); bl=[]
            sub=hdr.find("p"); 
            if sub: bl.append({"type":"p","text":text(sub),"html":"<p>"+clean(sub)+"</p>"})
            for ch in a.children:
                if getattr(ch,"name",None) in(None,"header"): continue
                bl.extend(blocks_of(BeautifulSoup("<div>%s</div>"%str(ch),"lxml").div))
            im=hdr.find("img")
            secs.append({"id":a.get("id"),"heading":text(h),"icon":im.get("src") if im else None,"blocks":bl})
        secs.append({"id":None,"heading":None,"blocks":[]}); secs.pop()
        for sec in kids[1:]:
            if sec.name=="section":
                hh=sec.find("h2"); 
                body=BeautifulSoup("<div>%s</div>"%"".join(str(c) for c in sec.children if c is not hh),"lxml").div
                secs.append({"id":"how-to-read","heading":text(hh),"blocks":blocks_of(body)})
        P["sections"]=secs; P["toc"]=[{"id":x["id"],"text":x["heading"]} for x in secs if x["id"]]
        P["title"]="Odds & luck"; hd=s.find("main").find("header"); P["subtitle"]=text(hd.find("p")); P["declared_count"]=int(text(hd.find("h1").find("span")))
        P["group_tabs_at_source"]=groups
    elif url=="/en/news":
        main=s.find("main"); secs=[]
        sec0=main.find("article").find_parent("section")
        lead=[{"type":"p","text":text(p),"html":"<p>"+clean(p)+"</p>"} for p in sec0.find_all("p",recursive=False)] if sec0 else []
        if lead: secs.append({"id":None,"heading":None,"blocks":lead})
        for a in main.find_all("article"):
            h=a.find("h2"); secs.append({"id":None,"heading":text(h) if h else None,"blocks":blocks_of(a)})
        P["sections"]=secs
        hd=main.find("header") or main.find("h1").parent
        P["title"]=text(main.find("h1")); P["subtitle"]=text(main.find("h1").find_next("p"))
    else:
        # listing / no h2 pages: keep whole article body blocks
        P["sections"]=[{"id":None,"heading":None,"blocks":blocks_of(art)}]
    # related
    rel=None
    for sec in art.find_all("section"):
        h=sec.find("h2")
        if h and text(h)=="Related pages": rel=sec
    P["related"]=[{"text":text(a),"href":a["href"],"img":(a.find("img") or {}).get("src") if a.find("img") else None} for a in rel.find_all("a")] if rel else []
    P["toc"]=[{"id":a.get("data-toc"),"text":text(a)} for a in art.find_all("a",attrs={"data-toc":True})]
    P["images"]=sorted({i["src"] for i in art.find_all("img") if i.get("src")})
    P["links"]=sorted({a["href"].split("#")[0].split("?")[0] for a in art.find_all("a",href=True) if a["href"].startswith("/")})
    pages.append(P)
json.dump(pages,open("/home/claude/overrank/data/extract_raw.json","w"),ensure_ascii=False)
print("pages",len(pages),"errors",sum(1 for p in pages if p.get("error")))
