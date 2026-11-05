import json, re, glob, os
from bs4 import BeautifulSoup
R="/home/claude/overrank"
# ---- codes from news
idx=json.load(open(R+"/db/entities/news/index.json"))
codes={}
blocks=[b for s in idx["sections"] for b in s["blocks"]]
cur={}
for b in blocks:
    if b["type"]=="div" and re.match(r"Code ·",b["text"]): cur={"published_text":b["text"].split("·")[1].strip()}
    elif b["type"]=="h2":
        a=BeautifulSoup(b["html"],"lxml").find("a")
        cur["news_path"]=a["href"] if a else None; cur["news_title"]=b["text"]
    elif b["type"]=="div" and "<code>" in b["html"]:
        x=BeautifulSoup(b["html"],"lxml"); sp=[t.get_text(strip=True) for t in x.find_all("span")]
        cur["code"]=x.find("code").get_text(strip=True); cur["status_at_source"]=sp[0] if sp else None; cur["rewards"]=sp[1] if len(sp)>1 else None
        codes[cur["code"]]=dict(cur); cur={}
# detail posts: date + rewards
for f in glob.glob(R+"/db/entities/news/*.json"):
    e=json.load(open(f))
    if e["slug"]=="index": continue
    bl=[b for s in e["sections"] for b in s["blocks"]]
    code=next((b["text"] for b in bl if b["type"]=="code"),None)
    date=next((b["text"].split("·")[0].strip() for b in bl if b["type"]=="div" and "·" in b["text"] and re.search(r"20\d\d",b["text"])),None)
    rew=next((b["text"] for b in bl if b["type"]=="p"),None)
    if code:
        c=codes.setdefault(code,{"code":code})
        c.update(news_path=e["source"]["path"],detail_date=date,detail_rewards=rew,news_id=e["id"])
# ---- homepage
s=BeautifulSoup(open(R+"/raw/pages/en.html",encoding="utf-8").read(),"lxml"); m=s.find("main")
for t in m.find_all(["svg","script","style"]): t.decompose()
def sec(name):
    h=[x for x in m.find_all("h2") if x.get_text(strip=True).startswith(name)][0]
    return h.find_parent("section") or h.parent.parent
home={"source":"https://overrank.awaitlab.com/en","tagline":"Classes, ranks, rifts, items. Ask a question or browse the wiki."}
home["start_here"]=[{"href":a["href"],"image":a.find("img")["src"],"title":a.find_all("span")[0].get_text(strip=True),"text":a.find_all("span")[1].get_text(strip=True)} for a in sec("Start here").find_all("a")]
act=[]
for li in sec("Active codes").find_all("li"):
    a=li.find("a"); p=li.find("p").get_text(" ",strip=True)
    mm=re.match(r"Ends (.*?) · (.*)$",p)
    act.append({"code":a.get_text(strip=True),"news_path":a["href"],"ends_text":mm.group(1) if mm else None,"rewards":mm.group(2) if mm else p})
home["active_codes_at_crawl"]=act
pop=[]
for a in sec("Popular pages").find_all("a"):
    sp=a.find_all("span"); 
    pop.append({"href":a["href"],"image":a.find("img")["src"],"title":sp[1].get_text(strip=True),"category":sp[2].get_text(strip=True),"badge":sp[3].get_text(strip=True) if len(sp)>3 else None})
home["popular_at_crawl"]=pop
for a in act:
    c=codes.setdefault(a["code"],{"code":a["code"]}); c["ends_text"]=a["ends_text"]; c["listed_active_at_crawl"]=True
json.dump(sorted(codes.values(),key=lambda c:c.get("code")),open(R+"/db/codes.json","w"),ensure_ascii=False,indent=1)
json.dump(home,open(R+"/db/home.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(sorted(codes.values(),key=lambda c:c['code']),ensure_ascii=False)[:1800])
print(len(codes),"codes;",len(home["start_here"]),"start;",len(pop),"popular")
