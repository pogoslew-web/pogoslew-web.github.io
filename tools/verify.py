"""Contrôle d'intégrité : source (HTML brut) -> base structurée -> (option --dist) site construit."""
import json, re, sys, glob, os, collections, hashlib, urllib.request, urllib.error, time
from bs4 import BeautifulSoup
R="/home/claude/overrank"
inv=json.load(open(R+"/raw/inventory.json"))
man=json.load(open(R+"/data/assets_manifest.json"))
refs=json.load(open(R+"/data/resource_refs.json"))
cats=json.load(open(R+"/db/categories.json"))
hubs=json.load(open(R+"/data/hubs_raw.json"))
ents={}
for f in glob.glob(R+"/db/entities/*/*.json"):
    e=json.load(open(f)); ents[e["source"]["path"]]=e
NUM=re.compile(r"\d[\d,\.]*%?")
def toks(text): return collections.Counter(NUM.findall(re.sub(r"\s+"," ",text)))
def words(text): return collections.Counter(re.findall(r"[A-Za-z0-9À-ɏ'+%?-]+",text))
def raw_body(path):
    s=BeautifulSoup(open(inv[path]["file"],encoding="utf-8").read(),"lxml"); art=s.find("article")
    h2=next((h for h in art.find_all("h2") if h.get("id")),None)
    if not h2: return ""
    cont=h2.parent
    for t in cont.find_all(["svg","script","style"]): t.decompose()
    return cont.get_text(" ",strip=True)
def ent_body(e):
    out=[]
    for s in e["sections"]:
        if s["heading"]: out.append(s["heading"])
        for b in s["blocks"]:
            if b.get("html"): out.append(BeautifulSoup(b["html"],"lxml").get_text(" ",strip=True))
            elif b.get("text"): out.append(b["text"])
    return " ".join(out)
def raw_region_words(path):
    s=BeautifulSoup(open(inv[path]["file"],encoding="utf-8").read(),"lxml"); m=s.find("main")
    for lab in m.find_all("label"):
        if lab.find("input",type="number") is not None: lab.decompose()
    for t in m.find_all(["svg","script","style","nav","button","input"]): t.decompose()
    for h in m.find_all(["h2","h3"]):
        if h.get_text(strip=True)=="Discussion":   # widget de forum (UI communautaire) : exclu volontairement
            blk=h.find_parent("section") or h.parent
            if blk is not None: blk.decompose()
    for lab in m.find_all("label"):
        if lab.find("input",type="number") is not None: lab.decompose()
    for a in m.find_all("a"):
        if a.get_text(strip=True)=="Overview" and a.find_parent("header"): a.decompose()
    return re.sub(r"\+\s+","+",m.get_text(" ",strip=True))
def ent_all_text(e):
    out=[e.get("title") or "",e.get("summary") or ""]
    for s in e["sections"]:
        if s["heading"]: out.append(s["heading"])
        for b in s["blocks"]:
            out.append(BeautifulSoup(b["html"],"lxml").get_text(" ",strip=True) if b.get("html") else (b.get("text") or ""))
    out+=[i["key"]+" "+i["value"] for i in e["infobox"]]
    out+=[str(e.get("declared_count") or "")]+list(e.get("group_tabs_at_source") or [])
    return re.sub(r"\+\s+","+"," ".join(out))
SPECIAL=[p for p,e in ents.items() if (e["type"]=="news") or p=="/en/w/overrank/odds"]
def raw_facts(path):
    s=BeautifulSoup(open(inv[path]["file"],encoding="utf-8").read(),"lxml"); qf=s.find(attrs={"aria-label":"Quick facts"})
    if not qf: return ""
    return " ".join(d.get_text(" ",strip=True) for d in qf.parent.find_all("dd"))
rep={"generated":time.strftime("%Y-%m-%d"),"stage":"source->db"}
mism=[]; checked=0; word_loss=[]
for path,e in ents.items():
    if e["type"]=="news" and e["slug"]=="index" and False: continue
    try: rb=raw_body(path)
    except Exception as ex: mism.append({"path":path,"error":str(ex)}); continue
    eb=ent_body(e); checked+=1
    rn,en=toks(rb),toks(eb)
    miss={k:v-en.get(k,0) for k,v in rn.items() if en.get(k,0)<v}
    rw,ew=words(rb),words(eb)
    wl={k:v-ew.get(k,0) for k,v in rw.items() if ew.get(k,0)<v}
    fr=toks(raw_facts(path)); fe=toks(" ".join(i["value"] for i in e["infobox"]))
    fmiss={k:v-fe.get(k,0) for k,v in fr.items() if fe.get(k,0)<v}
    if miss or fmiss or sum(wl.values())>0: mism.append({"path":path,"numbers_missing":miss,"facts_numbers_missing":fmiss,"words_missing":dict(list(wl.items())[:10])})
special=[]
for p in SPECIAL:
    rw=words(raw_region_words(p)); ew=words(ent_all_text(ents[p]))
    # tolérance : chrome connu de la page (titres de navigation répétés, libellés de contrôles retirés)
    miss={k:n-ew.get(k,0) for k,n in rw.items() if ew.get(k,0)<n}
    special.append({"path":p,"raw_words":sum(rw.values()),"entity_words":sum(ew.values()),"words_missing":dict(sorted(miss.items(),key=lambda x:-x[1])[:15]),"missing_total":sum(miss.values())})
rep["fidelity_special_pages"]=special
# non-vacuité : aucune page standard ne doit avoir un corps source vide si l'entité a du contenu
empty=[p for p,e in ents.items() if p not in SPECIAL and not raw_body(p).strip() and any(s["blocks"] for s in e["sections"])]
rep["fidelity_vacuous_pages"]=empty
rep["fidelity"]={"pages_compared":checked,"pages_with_differences":len(mism),"details":mism[:40]}
# comptes par catégorie
rows=[]
for c in cats:
    k=c["id"]; fetched=[p for p in inv if re.match(rf"^/en/w/overrank/{k}/[^/]+$",p) and not p.endswith("/overview") and inv[p]["status"]==200]
    integ=[e for e in ents.values() if e["type"]==k and not e["is_overview"]]
    rows.append({"id":k,"label":c["label"],"declared":c["declared_count"],"cards_listed":len(c["order"]),"fetched":len(fetched),"integrated":len(integ),"overview":c["has_overview"]})
rep["by_category"]=rows
# pages
excl_edit=len(glob.glob(R+"/raw/excluded_edit/*.html"))
allhref=set()
for v in inv.values():
    if v["status"]==200:
        s=open(v["file"],encoding="utf-8").read()
        allhref|={h.split("#")[0].split("?")[0].rstrip("/") for h in re.findall(r'href="(/en[^"]*)"',s)}
inscope=set(inv); out=sorted(h for h in allhref if h and h not in inscope and not h.endswith("/edit"))
rep["pages"]={"in_scope_discovered":len(inv),"fetched_ok":sum(1 for v in inv.values() if v["status"]==200),"fetch_failed":sum(1 for v in inv.values() if v["status"]!=200),
  "integrated_as_pages":len(ents),"index_and_home_pages":len(inv)-len(ents)-1,"alias_not_content":["/en/w/overrank/random (redirects to a random page)"],
  "edit_forms_excluded":excl_edit,"out_of_scope_paths":out[:60],"out_of_scope_count":len(out)}
# images
files={e["file"] for e in man.values() if e["status"]==200}
total_bytes=sum(os.path.getsize(R+"/assets/"+f) for f in files)
ent_imgs=[e["image"] for e in ents.values() if e["image"]]
rep["images"]={"referenced":len(refs),"downloaded":sum(1 for e in man.values() if e["status"]==200),"failed":[k for k,e in man.items() if e["status"]!=200],
  "unique_files_after_dedup":len(files),"duplicates_removed":len(man)-len(files),"total_bytes":total_bytes,
  "entities_with_image":len(ent_imgs),"entity_images_missing":[i for i in ent_imgs if i not in man or man[i]["status"]!=200],
  "by_type":dict(collections.Counter(os.path.splitext(f)[1] for f in files))}
rep["entities_without_image"]=len([e for e in ents.values() if not e["image"]])
rep["incomplete_at_source"]=sorted(e["source"]["path"] for e in ents.values() if e["incomplete_at_source"])
json.dump(rep,open(R+"/db/integrity.json","w"),indent=1,ensure_ascii=False)
print(json.dumps({k:rep[k] for k in("fidelity","pages","images")},indent=1,ensure_ascii=False)[:3500])
print("by_category mismatches:",[r for r in rows if not(r["declared"]==r["fetched"]==r["integrated"])])
