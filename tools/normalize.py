import json, re, os, collections
R="/home/claude/overrank"
P=json.load(open(R+"/data/extract_raw.json")); H=json.load(open(R+"/data/hubs_raw.json"))
os.makedirs(R+"/db/entities",exist_ok=True)
WIKI="/en/w/overrank"
LABEL={"guides":"Guides","systems":"Systems","classes":"Classes","skills":"Skills","weapon-arts":"Weapon arts","passives":"Passives","items":"Items","cosmetics":"Cosmetics","monsters":"Monsters","rifts":"Rifts","dungeons":"Dungeons","places":"Places","ranks":"Ranks","titles":"Titles","odds":"Odds & luck","formulas":"Formulas","events":"Events","passes":"Game passes","products":"Shop products","badges":"Badges","glossary":"Glossary"}
FAMILY={"classes":"Gameplay","skills":"Gameplay","weapon-arts":"Gameplay","passives":"Gameplay","systems":"Gameplay",
 "ranks":"Progression","titles":"Progression","badges":"Progression",
 "items":"Database","cosmetics":"Database",
 "rifts":"World","dungeons":"World","places":"World","monsters":"World",
 "guides":"Guides",
 "events":"Extra","passes":"Extra","products":"Extra","glossary":"Extra","formulas":"Extra","odds":"Extra"}
RARITY_KEYS=["Rank / rarity","Rarity","Grade","Rank"]
def fix_date(d): return re.sub(r"\s*Edit$","",d or "").strip() or None
ents={}; alias={}
for p in P:
    path=p["path"]
    if p.get("error"): continue
    if path==WIKI+"/random": alias[path]="redirect to a random page (not content)"; continue
    m=re.match(r"/en/w/overrank/([^/]+)/([^/]+)$",path)
    if m: typ,slug=m.group(1),m.group(2)
    elif path==WIKI+"/odds": typ,slug="odds","index"
    else:
        m2=re.match(r"/en/news/([^/]+)$",path)
        if m2: typ,slug="news",m2.group(1)
        elif path=="/en/news": typ,slug="news","index"
        else: typ,slug="page",path.strip("/").replace("/","-")
    eid=f"{typ}/{slug}"
    ib=p.get("infobox") or []
    rar=next((i["value"] for k in RARITY_KEYS for i in ib if i["key"]==k),None)
    heads=[s["heading"] for s in p["sections"] if s["heading"]]
    e={"id":eid,"type":typ,"slug":slug,"title":p.get("title"),"summary":p.get("subtitle"),"rarity":rar,
       "is_overview":slug=="overview","image":(p.get("image") or {}).get("src"),
       "infobox":[{"key":i["key"],"value":i["value"],"html":i["html"]} for i in ib],
       "sections":p["sections"],"media":[{"src":x["src"],"alt":x.get("alt"),"kind":"3d-model"} for x in p.get("extra_media",[])],
       "related":p.get("related",[]),"toc":p.get("toc",[]),
       "last_edited":fix_date(p.get("last_edited")),"last_edited_by":p.get("last_edited_by"),
       "incomplete_at_source":any(h in("What we know","Complete this page") for h in heads),
       "source":{"url":p["url"],"path":path},"raw_links":p.get("links",[]),"declared_count":p.get("declared_count"),"group_tabs_at_source":p.get("group_tabs_at_source")}
    ents[eid]=e
# resolve links
path2id={e["source"]["path"]:e["id"] for e in ents.values()}
edges=set()
for e in ents.values():
    out=set()
    for l in e["raw_links"]+[r["href"] for r in e["related"]]:
        l=l.rstrip("/")
        if l in path2id and path2id[l]!=e["id"]: out.add(path2id[l])
    e["links_to"]=sorted(out)
    for t in out: edges.add((e["id"],t))
back=collections.defaultdict(set)
for a,b in edges: back[b].add(a)
for e in ents.values(): e["linked_from"]=sorted(back[e["id"]])
# categories
cats=[]
for h in H:
    m=re.match(r"/en/w/overrank/([^/]+)$",h["path"])
    if not m or not h["cards"]: continue
    k=m.group(1)
    cats.append({"id":k,"label":LABEL.get(k,h.get("title")),"family":FAMILY.get(k,"Extra"),"description":h.get("description"),
      "declared_count":h["declared_count"],"count":len([e for e in ents.values() if e["type"]==k and not e["is_overview"]]),
      "has_overview":f"{k}/overview" in ents,"source":{"url":h["url"]},
      "order":[c["href"].rstrip("/") for c in h["cards"]]})
# odds is an article page but is a category too
if "odds/index" in ents:
    cats.append({"id":"odds","label":"Odds & luck","family":"Extra","description":ents["odds/index"]["summary"],"declared_count":ents["odds/index"]["declared_count"],"count":sum(1 for sec in ents["odds/index"]["sections"] for b in sec["blocks"] if b["type"]=="table"),"has_overview":True,"source":{"url":ents["odds/index"]["source"]["url"]},"order":[]})
json.dump(cats,open(R+"/db/categories.json","w"),ensure_ascii=False,indent=1)
for e in ents.values():
    d=R+"/db/entities/"+e["type"]; os.makedirs(d,exist_ok=True)
    json.dump(e,open(f"{d}/{e['slug']}.json","w"),ensure_ascii=False)
json.dump(sorted(edges),open(R+"/db/relations.json","w"))
json.dump(alias,open(R+"/db/aliases.json","w"),indent=1)
print("entities",len(ents),"edges",len(edges),"types",dict(collections.Counter(e["type"] for e in ents.values())))
print("incomplete_at_source",sum(e["incomplete_at_source"] for e in ents.values()))
