import re, json
from bs4 import BeautifulSoup
inv=json.load(open("/home/claude/overrank/raw/inventory.json"))
def text(el): return re.sub(r"\s+"," ",el.get_text(" ",strip=True)).strip()
hubs=[]
for url,v in sorted(inv.items()):
    if v["status"]!=200: continue
    s=BeautifulSoup(open(v["file"],encoding="utf-8").read(),"lxml")
    if s.find("article"): continue
    m=s.find("main")
    for t in m.find_all(["svg","script","style"]): t.decompose()
    H={"path":url,"url":"https://overrank.awaitlab.com"+url,"title_tag":s.title.get_text()}
    h1=m.find("h1")
    if h1:
        sp=h1.find("span"); 
        H["declared_count"]=int(sp.get_text(strip=True)) if sp and sp.get_text(strip=True).isdigit() else None
        if sp: sp.extract()
        H["title"]=text(h1)
        p=h1.find_next("p"); H["description"]=text(p) if p else None
    cards=[]
    for li in m.find_all("li"):
        a=li.find("a",href=True)
        if not a or not li.find("h3"): continue
        im=a.find("img")
        cards.append({"href":a["href"],"title":text(li.find("h3")),"title_attr":(li.find("h3").get("title")),
          "img":im["src"] if im else None,"img_alt":im.get("alt") if im else None,
          "badges":[text(b) for b in a.find_all(class_="badge")],"text":text(a)})
    H["cards"]=cards
    H["main_text"]=re.sub(r"\n\s*\n+","\n",m.get_text("\n",strip=True))
    H["links"]=sorted({a["href"].split("#")[0].split("?")[0] for a in m.find_all("a",href=True) if a["href"].startswith("/")})
    H["images"]=sorted({i["src"] for i in m.find_all("img") if i.get("src")})
    H["tables"]=[]
    for t in m.find_all("table"):
        H["tables"].append({"headers":[text(th) for th in t.find_all("th")],"rows":[[text(td) for td in tr.find_all(["td","th"])] for tr in t.find_all("tr")]})
    hubs.append(H)
json.dump(hubs,open("/home/claude/overrank/data/hubs_raw.json","w"),ensure_ascii=False,indent=1)
for h in hubs: print(h["path"],h.get("declared_count"),len(h["cards"]),len(h["tables"]))
