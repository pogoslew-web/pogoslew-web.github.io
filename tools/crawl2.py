import re, sys, time, json, urllib.request, urllib.error, collections, os
BASE="https://overrank.awaitlab.com"
OUT=sys.argv[1]
UA="OverrankMirror/1.0 (personal reconstruction project; polite crawler)"
DELAY=0.6
ALLOW=re.compile(r'^/en(/w/overrank(/(?!.*/edit$).*)?|/news(/.*)?)?$')
def fn_of(p): return OUT+"/pages/"+(p.strip("/").replace("/","__") or "root")+".html"
def links_of(body):
    s=set()
    for l in re.findall(r'href="(/[^"#?]*)"',body):
        l=l.rstrip("/") or "/"
        if ALLOW.match(l): s.add(l)
    return s
inv={}
if os.path.exists(OUT+"/inventory.json"): inv=json.load(open(OUT+"/inventory.json"))
queue=collections.deque(["/en","/en/w/overrank","/en/news"])
seen=set()
def fetch(p):
    req=urllib.request.Request(BASE+p,headers={"User-Agent":UA,"Accept-Language":"en"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status,r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code,""
    except Exception as e: return 0,""
n=0
while queue:
    p=queue.popleft()
    if p in seen: continue
    seen.add(p)
    f=fn_of(p)
    if p in inv and inv[p]["status"] in (200,404): ls=inv[p]["links"]
    elif os.path.exists(f):
        body=open(f,encoding="utf-8").read(); ls=sorted(links_of(body)); inv[p]={"status":200,"file":f,"links":ls}
    else:
        st,body=fetch(p); time.sleep(DELAY)
        ls=sorted(links_of(body)) if st==200 else []
        if st==200: open(f,"w",encoding="utf-8").write(body)
        inv[p]={"status":st,"file":f if st==200 else None,"links":ls}
        n+=1; print(st,p,flush=True)
        if n%25==0: json.dump(inv,open(OUT+"/inventory.json","w"))
    for l in ls:
        if l not in seen: queue.append(l)
json.dump(inv,open(OUT+"/inventory.json","w"),indent=1)
print("TOTAL",len(inv),"OK",sum(1 for v in inv.values() if v["status"]==200),"NEWFETCH",n,flush=True)
