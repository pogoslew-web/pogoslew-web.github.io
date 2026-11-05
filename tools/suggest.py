"""Best-gear suggestions per class and rank, computed ONLY from site data.
Rule: among weapons of the class's weapon styles (and armors) obtainable at rank R (drop source text),
pick the highest base Attack (weapons) / base HP then damage reduction (armor). No invented value."""
import json,glob,re,os
R="/home/claude/overrank"
RANKS=["E","D","C","B","A","S","S+","Nation"]
def info(e): return {i["key"]:i["value"] for i in e["infobox"]}
def avail(e):
    t=" ".join(b.get("text","") for s in e["sections"] if (s.get("id") or "")=="how-to-get-it" for b in s["blocks"])
    if re.search(r"every rank",t): return "E",t
    m=re.findall(r"rank (Nation|S\+\+|S\+|S|A|B|C|D|E)\+? dungeons",t)
    if m:
        k=m[0]; k={"S++":"S+"}.get(k,k); return k,t
    return None,t
NATION_PRIZE=[]
items=[json.load(open(f)) for f in glob.glob(R+"/db/entities/items/*.json")]
W=[];A=[]
for e in items:
    i=info(e); k=i.get("Kind") or ""
    r,t=avail(e)
    ii=info(e)
    if r is None and (ii.get("Kind") or "").endswith("(weapon)") and ii.get("Attack") and "Nation edition" in (ii.get("Grade") or "") and "guardian spoils" in t:
        NATION_PRIZE.append({"slug":e["slug"],"title":e["title"],"style":ii["Kind"].split(" ")[0],"attack":float(ii["Attack"]),"image":e.get("image"),"stats":{x:ii[x] for x in("Attack","Crit chance %","Intelligence","Agility","Strength","Spirit","Vitality") if x in ii},"note":"Nation edition: rare guardian spoil (about 0.15% in a Nation dungeon, per its page)"})
    if r is None: continue
    rec={"slug":e["slug"],"title":e["title"],"min_rank":r,"image":e.get("image"),"rarity":e.get("rarity"),"grade":i.get("Grade")}
    if k.endswith("(weapon)") and i.get("Attack"):
        rec.update(style=k.split(" ")[0],attack=float(i["Attack"]),crit=float(i.get("Crit chance %") or 0),stats={x:i[x] for x in("Attack","Crit chance %","Intelligence","Agility","Strength","Spirit","Vitality") if x in i}); W.append(rec)
    elif k=="Armor" and i.get("HP"):
        rec.update(hp=float(i["HP"]),dr=float(i.get("Damage reduction %") or 0),stats={x:i[x] for x in("HP","Damage reduction %") if x in i}); A.append(rec)
def cls_types(slug):
    ov=json.load(open(R+"/db/overlays/class_cards.json"))["classes"]
    if slug in ov: return ov[slug]["weapons"],ov[slug]["armor"]
    i=info(json.load(open(f"{R}/db/entities/classes/{slug}.json")))
    sp=lambda s:[x.strip() for x in (s or "").split(",") if x.strip()]
    return sp(i.get("Weapons")),sp(i.get("Armor"))
out={"method":"Best base stat among gear obtainable at that rank (drop source text on each item page). Weapons: highest Attack among the class's weapon styles (ties: crit chance). Armor: highest HP (ties: damage reduction); the site does not tag armor types on item pages, so armor is not filtered by class. Base values are rank E / Common / +0; the real value scales with rank, grade and forge (see Items and forge formulas).",
"ranks":RANKS,"classes":{}}
for f in sorted(glob.glob(R+"/db/entities/classes/*.json")):
    slug=os.path.basename(f)[:-5]
    if slug=="overview": continue
    ws,ar=cls_types(slug)
    any_w=any(w.lower()=="any" for w in ws)
    rows=[]
    for rk in RANKS:
        n=RANKS.index(rk)
        ok=lambda x:RANKS.index(x["min_rank"])<=n
        cw=[w for w in W if ok(w) and (any_w or w["style"] in ws)]
        cw.sort(key=lambda w:(-w["attack"],-w["crit"],w["title"]))
        ca=sorted([a for a in A if ok(a)],key=lambda a:(-a["hp"],-a["dr"],a["title"]))
        row={"rank":rk,"weapon":cw[0] if cw else None,"armor":ca[0] if ca else None}
        if rk=="Nation":
            dz=sorted([w for w in NATION_PRIZE if any_w or w["style"] in ws],key=lambda w:(-w["attack"],w["title"]))
            row["dream_weapon"]=dz[0] if dz else None
        rows.append(row)
    out["classes"][slug]={"weapon_styles":ws,"armor_types":ar,"rows":rows}
json.dump(out,open(R+"/db/suggestions.json","w"),ensure_ascii=False,indent=1)
print(len(W),"weapons",len(A),"armors")
for s in ("assassin","tank","reaper"):
    for r in out["classes"][s]["rows"]: print(s,r["rank"],r["weapon"] and (r["weapon"]["title"],r["weapon"]["attack"]),r["armor"] and (r["armor"]["title"],r["armor"]["hp"]))
