import re, sys, time, json, urllib.request, urllib.error, collections, os
BASE="https://overrank.awaitlab.com"
OUT=sys.argv[1]
UA="OverrankMirror/1.0 (personal reconstruction project; polite crawler)"
DELAY=0.6
ALLOW=re.compile(r'^/en(/w/overrank(/.*)?|/news(/.*)?)?$')
seeds=["/en","/en/w/overrank","/en/news"]
seen=set(); queue=collections.deque(seeds); inv={}
os.makedirs(OUT+"/pages",exist_ok=True)
def fetch(p):
    req=urllib.request.Request(BASE+p,headers={"User-Agent":UA,"Accept-Language":"en"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            return r.status,r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code,""
    except Exception as e:
        return 0,str(e)
while queue:
    p=queue.popleft()
    if p in seen: continue
    seen.add(p)
    st,body=fetch(p)
    fn=OUT+"/pages/"+(p.strip("/").replace("/","__") or "root")+".html"
    if st==200: open(fn,"w",encoding="utf-8").write(body)
    links=set()
    if st==200:
        for l in re.findall(r'href="(/[^"#?]*)"',body):
            l=l.rstrip("/") or "/"
            if ALLOW.match(l): links.add(l)
    inv[p]={"status":st,"file":fn if st==200 else None,"links":sorted(links)}
    for l in links:
        if l not in seen: queue.append(l)
    print(st,p,len(links),flush=True)
    time.sleep(DELAY)
json.dump(inv,open(OUT+"/inventory.json","w"),indent=1)
print("TOTAL",len(inv),"OK",sum(1 for v in inv.values() if v["status"]==200))
