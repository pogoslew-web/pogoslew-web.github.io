import json, os, sys, time, hashlib, urllib.request, urllib.error, threading
from concurrent.futures import ThreadPoolExecutor
BASE="https://overrank.awaitlab.com"
ROOT="/home/claude/overrank"
refs=json.load(open(ROOT+"/data/resource_refs.json"))
os.makedirs(ROOT+"/assets/files",exist_ok=True)
MAN=ROOT+"/data/assets_manifest.json"
man=json.load(open(MAN)) if os.path.exists(MAN) else {}
UA="OverrankMirror/1.0 (personal reconstruction project; polite crawler)"
lock=threading.Lock(); last=[0.0]
EXT={"image/webp":".webp","image/png":".png","image/jpeg":".jpg","image/svg+xml":".svg","image/gif":".gif","image/avif":".avif","model/gltf-binary":".glb","application/octet-stream":".bin","video/mp4":".mp4","audio/mpeg":".mp3"}
def get(p):
    with lock:
        w=0.15-(time.time()-last[0]); 
        if w>0: time.sleep(w)
        last[0]=time.time()
    req=urllib.request.Request(BASE+p,headers={"User-Agent":UA})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            return r.status,r.headers.get("content-type","").split(";")[0],r.read()
    except urllib.error.HTTPError as e: return e.code,"",b""
    except Exception as e: return 0,"",b""
def work(p):
    if p in man and man[p].get("status")==200: return
    st,ct,data=get(p)
    e={"status":st,"content_type":ct,"used_on":refs[p]}
    if st==200:
        h=hashlib.sha256(data).hexdigest()
        ext=EXT.get(ct) or os.path.splitext(p)[1] or ".bin"
        fn=f"files/{h[:16]}{ext}"
        if not os.path.exists(ROOT+"/assets/"+fn): open(ROOT+"/assets/"+fn,"wb").write(data)
        e.update(sha256=h,file=fn,bytes=len(data))
    with lock: man[p]=e
todo=[p for p in refs if not (p in man and man[p].get("status")==200)]
print("todo",len(todo),flush=True)
done=0
with ThreadPoolExecutor(3) as ex:
    for i,_ in enumerate(ex.map(work,todo)):
        if i%100==0:
            with lock: json.dump(man,open(MAN,"w"))
            print(i,flush=True)
json.dump(man,open(MAN,"w"),indent=0)
ok=sum(1 for v in man.values() if v["status"]==200)
print("DONE",len(man),"ok",ok,"failed",len(man)-ok,flush=True)
