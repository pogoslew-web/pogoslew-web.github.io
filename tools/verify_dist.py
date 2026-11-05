import json, re, glob, os, collections
from bs4 import BeautifulSoup
R="/home/claude/overrank"; D=R+"/site/dist"
NUM=re.compile(r"\d[\d,\.]*%?")
ents=[json.load(open(f)) for f in glob.glob(R+"/db/entities/*/*.json")]
cats=json.load(open(R+"/db/categories.json"))
def exists(url):
    p=url.split("#")[0].split("?")[0]
    if not p.startswith("/"): return True
    f=D+p
    return os.path.isfile(f) or os.path.isfile(f.rstrip("/")+"/index.html") or os.path.isfile(D+p.rstrip("/")+".html")
expected=[]
for e in ents:
    if e["type"]=="news": expected.append(f"/news/{e['slug']}/" if e["slug"]!="index" else "/news/")
    elif e["type"]=="odds" and e["slug"]=="index": expected.append("/odds/")
    else: expected.append(f"/{e['type']}/{e['slug']}/")
expected+= [f"/{c['id']}/" for c in cats]+["/","/codes/","/database/","/search/","/random/","/leaderboards/","/integrity/","/404.html"]
missing=[u for u in set(expected) if not exists(u)]
numchk=0; nummiss=[]; pages=0
for e in ents:
    if e["type"]=="odds" and e["slug"]=="index": url="/odds/"
    elif e["type"]=="news" and e["slug"]=="index": url="/news/"
    elif e["type"]=="news": url=f"/news/{e['slug']}/"
    else: url=f"/{e['type']}/{e['slug']}/"
    f=D+url+"index.html"
    if not os.path.isfile(f): continue
    pages+=1
    s=BeautifulSoup(open(f,encoding="utf-8").read(),"lxml"); m=s.find("main")
    for t in m.find_all(["script","style"]): t.decompose()
    html_txt=m.get_text(" ",strip=True)
    if e["type"]=="news" and e["slug"]=="index":   # liste d'annonces : rendue par la page /news/ (titres + date), vérifiée via les posts
        continue
    src=[]
    for sec in e["sections"]:
        if sec["heading"]: src.append(sec["heading"])
        for b in sec["blocks"]:
            src.append(BeautifulSoup(b["html"],"lxml").get_text(" ",strip=True) if b.get("html") else (b.get("text") or ""))
    src+=[i["value"] for i in e["infobox"]]+[e.get("title") or "",e.get("summary") or ""]
    want=collections.Counter(NUM.findall(re.sub(r"\s+"," "," ".join(src)))); have=collections.Counter(NUM.findall(re.sub(r"\s+"," ",html_txt)))
    numchk+=sum(want.values())
    miss={k:v-have.get(k,0) for k,v in want.items() if have.get(k,0)<v}
    if miss: nummiss.append({"url":url,"missing":miss})
# liens internes et images
broken=set(); imgmiss=set(); links=0
for f in glob.glob(D+"/**/*.html",recursive=True):
    s=open(f,encoding="utf-8").read()
    for h in re.findall(r'href="(/[^"]*)"',s):
        links+=1
        if not exists(h): broken.add((f.replace(D,""),h))
    for h in re.findall(r'src="(/[^"]*)"',s):
        if h and not exists(h): imgmiss.add(h)
    for h in re.findall(r'data-missing="([^"]*)"',s): imgmiss.add("source-missing:"+h)
res={"pages_expected":len(set(expected)),"pages_checked":pages,"pages_missing":len(missing),"missing_list":missing[:20],
 "numbers_checked":numchk,"numbers_missing":sum(sum(d["missing"].values()) for d in nummiss),"pages_with_missing_numbers":nummiss[:15],
 "internal_links_checked":links,"broken_internal_links":len(broken),"broken_sample":sorted(broken)[:15],"images_missing":sorted(imgmiss)[:15],"images_missing_count":len(imgmiss),
 "html_pages_in_dist":len(glob.glob(D+"/**/*.html",recursive=True))}
json.dump(res,open(R+"/db/dist_check.json","w"),indent=1)
print(json.dumps({k:v for k,v in res.items() if k not in("missing_list",)},indent=1)[:2500])
