"""Traducteur à règles pour les phrases formulaïques du wiki (stats, listes de récompenses, potions…).
Strict : renvoie None si un mot anglais minuscule reste -> le gabarit part en traduction manuelle."""
import re
NB=' '
STATS={
 'damage reduction':'réduction de dégâts','magic damage':'dégâts magiques','physical damage':'dégâts physiques','critical damage':'dégâts critiques',
 'critical chance':'chance critique','max HP regen per second':'régénération de PV max par seconde','of max HP per second':'des PV max par seconde','max HP':'PV max','max mana':'mana max',
 'mana regeneration':'régénération de mana','mana regen per second':'régénération de mana par seconde','attack speed':'vitesse d’attaque','faster cooldowns':'recharge plus rapide','cooldowns':'temps de recharge',
 'boost duration':'durée des boosts','area of effect':'zone d’effet','heals and boosts':'soins et boosts','life steal':'vol de vie','luck':'chance','walking speed':'vitesse de marche',
 'move speed':'vitesse de déplacement','all stats':'toutes les stats','undead power':'puissance des morts-vivants','evasion':'esquive','damage':'dégâts','weapon damage':'dégâts d’arme',
 'shards':'éclats','XP':'XP','healing power':'puissance de soin','dodge speed':'vitesse d’esquive','experience':'expérience','XP and shards':'XP et éclats','XP or shards':'XP ou éclats','magic power':'puissance magique',
}
LEVEL={'levels':'niveaux','level':'niveau'}
def de(s): return ('d’' if re.match(r'[aeiouyéèêâhAEIOUÉ]',s) and not s.startswith(('h','H')) else 'de ')+s
SK=sorted(STATS,key=len,reverse=True)
S_RE='|'.join(re.escape(k) for k in SK)
RULES=[
 (r'([+-])⟦(\d+)⟧% of max HP per second',lambda m:f'{m[1]}⟦{m[2]}⟧{NB}% des PV max par seconde'),
 (r'([+-])⟦(\d+)⟧% ('+S_RE+r')\b',lambda m:f'{m[1]}⟦{m[2]}⟧{NB}% {de(STATS[m[3]])}'),
 (r'([+-])⟦(\d+)⟧ ('+S_RE+r')\b',lambda m:f'{m[1]}⟦{m[2]}⟧ {de(STATS[m[3]])}'),
 (r'At maximum level \(⟦(\d+)⟧\): ',lambda m:f'Au niveau maximum (⟦{m[1]}⟧) : '),
 (r'⟦(\d+)⟧% \(capped\)',lambda m:f'⟦{m[1]}⟧{NB}% (plafonné)'),
 (r'⟦(\d+)⟧% of (best|magic|physical) power',lambda m:f'⟦{m[1]}⟧{NB}% de la puissance '+{'best':'la plus forte','magic':'magique','physical':'physique'}[m[2]]),
 (r'\(up to ((?:\+⟦\d+⟧[^,()]*(?:, )?)+)\)',lambda m:'(jusqu’à '+m[1]+')'),
 (r' Forever\.',' Pour toujours.'),
 (r' <strong>per level</strong>',' <strong>par niveau</strong>'),(r' per level',' par niveau'),(r' per point',' par point'),
 (r'\(max ⟦(\d+)⟧%\)',lambda m:f'(max ⟦{m[1]}⟧{NB}%)'),(r'\(max ⟦(\d+)⟧\)',lambda m:f'(max ⟦{m[1]}⟧)'),
 (r'\(⟦(\d+)⟧ levels, tier ⟦(\d+)⟧ of the ([A-Za-z]+) tree\)',lambda m:f'(⟦{m[1]}⟧ niveaux, palier ⟦{m[2]}⟧ de l’arbre {m[3]})'),
 (r'\(⟦(\d+)⟧ levels\)',lambda m:f'(⟦{m[1]}⟧ niveaux)'),
 (r'for ⟦(\d+)⟧ s\.',lambda m:f'pendant ⟦{m[1]}⟧ s.'),
 (r'⟦(\d+)⟧ s cooldown, one potion at a time, ⟦(\d+)⟧ carried at most\.',lambda m:f'Recharge de ⟦{m[1]}⟧ s, une potion à la fois, ⟦{m[2]}⟧ portées au maximum.'),
 (r'An elixir: only at the traveling merchant, once per merchant\.','Un élixir : uniquement chez le marchand itinérant, une fois par marchand.'),
 (r'\bShards\b','Éclats'),(r'\bshards\b','éclats'),(r'XP/Éclats/Luck','XP/Éclats/Chance'),(r'XP/Shards/Luck','XP/Éclats/Chance'),
 (r', item ',', objet '),(r', cosmetic ',', cosmétique '),(r'(?<![\w>])cosmetic ','cosmétique '),(r', title ',', titre '),(r', class weapon \(grade',', arme de classe (grade'),
 (r'\+⟦(\d+)⟧ pass level',lambda m:f'+⟦{m[1]}⟧ niveau de pass'),(r'\+⟦(\d+)⟧ bag slots',lambda m:f'+⟦{m[1]}⟧ emplacements de sac'),(r'\+⟦(\d+)⟧ battle pass level\(s\)',lambda m:f'+⟦{m[1]}⟧ niveau(x) de pass de combat'),
 (r'⟦(\d+)⟧ side branch\(es\), ⟦(\d+)⟧ loops, ⟦(\d+)⟧ dead ends',lambda m:f'⟦{m[1]}⟧ branche(s) latérale(s), ⟦{m[2]}⟧ boucles, ⟦{m[3]}⟧ impasses'),
 (r'⟦(\d+)⟧ blast\(s\) ⟦(\d+)⟧ studs ahead \(⟦(\d+)⟧ studs\): ',lambda m:f'⟦{m[1]}⟧ explosion(s) à ⟦{m[2]}⟧ studs devant (⟦{m[3]}⟧ studs) : '),
 (r'Strikes ahead: ','Frappe devant : '),(r'Strikes in a line \(⟦(\d+)⟧ studs\): ',lambda m:f'Frappe en ligne (⟦{m[1]}⟧ studs) : '),
 (r'Hits all around \(⟦(\d+)⟧ studs\): ',lambda m:f'Frappe tout autour (⟦{m[1]}⟧ studs) : '),
 (r'Fires ⟦(\d+)⟧ projectile\(s\): ',lambda m:f'Tire ⟦{m[1]}⟧ projectile(s) : '),(r'A field \(⟦(\d+)⟧ studs\) for ⟦(\d+)⟧ s: ',lambda m:f'Un champ (⟦{m[1]}⟧ studs) pendant ⟦{m[2]}⟧ s : '),
 (r'⟦(\d+)⟧% (physical or magic \(your stronger one\)|physical|magic) damage( each| every ⟦\d+⟧ s)?',lambda m:f'⟦{m[1]}⟧{NB}% de dégâts '+{'physical':'physiques','magic':'magiques'}.get(m[2],'physiques ou magiques (le plus fort des deux)')+(' chacun' if m[3]==' each' else (' toutes les'+m[3][6:] if m[3] else ''))),
 (r'Knocks enemies back\.','Repousse les ennemis.'),(r'Pulls enemies in\.','Attire les ennemis.'),(r'Goes through every enemy\.','Traverse tous les ennemis.'),
 (r'Stuns for ⟦(\d+)⟧ s\.',lambda m:f'Étourdit pendant ⟦{m[1]}⟧ s.'),(r'Slows by ⟦(\d+)⟧% for ⟦(\d+)⟧ s\.',lambda m:f'Ralentit de ⟦{m[1]}⟧{NB}% pendant ⟦{m[2]}⟧ s.'),
 (r'Burns for ⟦(\d+)⟧% more over ⟦(\d+)⟧ s\.',lambda m:f'Brûle pour ⟦{m[1]}⟧{NB}% de plus sur ⟦{m[2]}⟧ s.'),(r'Heals you for ⟦(\d+)⟧% of the damage\.',lambda m:f'Vous soigne de ⟦{m[1]}⟧{NB}% des dégâts.'),
 (r'Each hit heals ⟦(\d+)⟧% of max HP\.',lambda m:f'Chaque coup soigne ⟦{m[1]}⟧{NB}% des PV max.'),(r'Dashes ⟦(\d+)⟧ studs forward\.',lambda m:f'Charge de ⟦{m[1]}⟧ studs vers l’avant.'),
 (r'Untouchable for ⟦(\d+)⟧ s\.',lambda m:f'Intouchable pendant ⟦{m[1]}⟧ s.'),(r'Bursts on impact \(⟦(\d+)⟧ studs\)\.',lambda m:f'Explose à l’impact (⟦{m[1]}⟧ studs).'),
 (r'Holds them in place for ⟦(\d+)⟧ s \(they can still strike\)\.',lambda m:f'Les immobilise pendant ⟦{m[1]}⟧ s (ils peuvent encore frapper).'),
 (r'Hits ⟦(\d+)⟧ times\.',lambda m:f'Touche ⟦{m[1]}⟧ fois.'),(r'Costs ⟦(\d+)⟧% of your max HP\.',lambda m:f'Coûte ⟦{m[1]}⟧{NB}% de vos PV max.'),
 (r'Teleports up to ⟦(\d+)⟧ studs\.',lambda m:f'Se téléporte jusqu’à ⟦{m[1]}⟧ studs.'),(r'Lands behind the nearest enemy ahead\.','Atterrit derrière l’ennemi le plus proche devant vous.'),
 (r'Class: ','Classe : '),(r'All skills of the class: ','Toutes les compétences de la classe : '),
 (r'⟦(\d+)⟧ x ','⟦\\1⟧ x '),
]
CR=[(re.compile(p),r) for p,r in RULES]
OK_WORDS=set('''maximum minimum normal special mana max boosts total type xp boost rift summon private anomaly server luck shard nation tank mage rank tier max min studs stat stats pass vip shards trash tower endless
 ticket bag slot slots gem arm armor aura edge weapon pendant item items epic rare common legendary mythic limited html strong span div img alt src href class
 les des une aux dans pour sur par avec sans est sont que qui plus pas vos votre vous leur ses son sa'''.split())
def clean(s): return re.sub(r'⟦\d+⟧|<[^>]*>|&\w+;','',s)
def auto(t):
    parts=re.split(r'(<[^>]*>)',t); out=[]
    for part in parts:
        if part.startswith('<'): out.append(part); continue
        x=part
        for rx,rep in CR: x=rx.sub(rep,x)
        out.append(x)
    s=''.join(out)
    if s==t: return None
    left=[w for w in re.findall(r'(?<![\w’])[a-z]{3,}',clean(s)) if w in set(re.findall(r'[a-z]{3,}',clean(t))) and w not in OK_WORDS]
    return None if left else s

LAB={'Accessory':'Accessoire','Armor':'Armure','Pendant':'Pendentif','Attack':'Attaque','Strength':'Force','Agility':'Agilité','Vitality':'Vitalité','Spirit':'Esprit','Defense':'Défense','Intelligence':'Intelligence','Perception':'Perception','HP':'PV','Crit chance %':'Chance critique %','Damage reduction %':'Réduction de dégâts %'}
KIND={'Armor':'armure','Weapon':'arme','Pendant':'pendentif','Aura':'aura','Edge':'edge'}
RAR={'Common':'Common','Rare':'Rare','Epic':'Epic','Legendary':'Legendary','Mythic':'Mythic','Limited':'Limited'}
def statline(t):
    m=re.fullmatch(r'(Accessory|Armor|Pendant|[A-Z][a-z]+ \(weapon\)) · (.+)',t)
    if not m: return None
    head=m[1]; head=LAB.get(head, head.replace('(weapon)','(arme)'))
    out=[head]
    for part in m[2].split(' · '):
        mm=re.fullmatch(r'(max \+⟦\d+⟧)|([A-Za-z %]+): (⟦\d+⟧)',part)
        if not mm: return None
        if mm[1]: out.append(mm[1])
        else:
            if mm[2] not in LAB: return None
            out.append(f'{LAB[mm[2]]} : {mm[3]}')
    return ' · '.join(out)
def cosm(t):
    m=re.fullmatch(r'(Armor|Weapon|Pendant|Aura|Edge) cosmetic \((\w+)\)\. Class rank: reach rank (\w\+?) as ([\w-]+)\.',t)
    if not m: return None
    k={'Armor':'Cosmétique d’armure','Weapon':'Cosmétique d’arme','Pendant':'Cosmétique de pendentif','Aura':'Aura cosmétique','Edge':'Edge cosmétique'}[m[1]]
    return f'{k} ({m[2]}). Rang de classe : atteindre le rang {m[3]} en tant que {m[4]}.'

KINDS={'Accessory':('Accessoire','il','Un'),'Armor':('Armure','elle','Une'),'Pendant':('Pendentif','il','Un')}
def item_sentence(t):
    m=re.fullmatch(r'<p>(Accessory|Armor|Pendant|(\w+) weapon)\. (.*)</p>',t)
    if not m: return None
    if m[2]: head,pr,un=f'Arme {m[2]}','elle','Une'
    else: head,pr,un=KINDS[m[1]]
    r=m[3]
    a=re.fullmatch(r'An <strong>(Nation|S\+) edition</strong>: it shows <strong>(Nation|S\+)</strong> instead of its grade letter and keeps its edition color, but its grade \(Trash F to Mythic S\) is still rolled when it drops and sets its stats\.',r)
    if a: return f'<p>{head}. {un} <strong>édition {a[1]}</strong> : {pr} affiche <strong>{a[2]}</strong> à la place de sa lettre de grade et garde la couleur de son édition, mais son grade (de Trash F à Mythic S) est toujours tiré à l’obtention et fixe ses stats.</p>'
    if r=='An <strong>SP</strong> edition: an exclusive reward between S and EX. Only the profile that earned a copy can trade, sell or auction it (two confirmations).':
        return f'<p>{head}. Une édition <strong>SP</strong> : une récompense exclusive entre S et EX. Seul le profil qui en a gagné un exemplaire peut l’échanger, le vendre ou le mettre aux enchères (deux confirmations).</p>'
    if r=='A <strong>Limited (EX)</strong> edition: never in the shops. Only the profile that earned a copy can trade, sell or auction it (two confirmations).':
        return f'<p>{head}. Une édition <strong>Limited (EX)</strong> : jamais en boutique. Seul le profil qui en a gagné un exemplaire peut l’échanger, le vendre ou le mettre aux enchères (deux confirmations).</p>'
    d=re.fullmatch(r'Its grade is rolled when it drops, from Trash \(F\) to Mythic \(S\); at \+⟦(\d+)⟧ the forge can raise it one grade at a time \(see ⟦(\d+)⟧\)\.',r)
    if d: return f'<p>{head}. Son grade est tiré à l’obtention, de Trash (F) à Mythic (S) ; à +⟦{d[1]}⟧ la forge peut l’améliorer d’un grade à la fois (voir ⟦{d[2]}⟧).</p>'
    return None
def misc(t):
    m=re.fullmatch(r'(<span><span>)?class rank: reach rank (\w\+?) as ([\w-]+)(</span></span>)?',t)
    if m: return f'{m[1] or ""}rang de classe : atteindre le rang {m[2]} en tant que {m[3]}{m[4] or ""}'
    m=re.fullmatch(r'Chest tiers, rank (\w+\+?) dungeon',t)
    if m: return f'Paliers de coffre, donjon de rang {m[1]}'
    m=re.fullmatch(r'(<p>)?Be reevaluated as a rank (\w\+?) awakened at the Registry\.(</p>)?',t)
    if m: return f'{m[1] or ""}Être réévalué éveillé de rang {m[2]} au Registre.{m[3] or ""}'
    return None


BOARD={'Highest level':'Niveau le plus élevé','Awakened slain':'Éveillés tués','Dungeons cleared':'Donjons terminés','Shards earned (all time)':'Éclats gagnés (total)','Monsters slain':'Monstres tués','Time played':'Temps de jeu','Global ranking':'Classement global','Colosseum victories':'Victoires au Colisée','Top donors':'Meilleurs donateurs','Endless Tower':'Tour infinie'}
def misc2(t):
    m=re.fullmatch(r'(<p>)?Hold a place from #⟦(\d+)⟧ to #⟦(\d+)⟧ on the board "(.+)" \(all servers\)\.(</p>)?',t)
    if m and m[4] in BOARD: return f'{m[1] or ""}Occupez une place de #⟦{m[2]}⟧ à #⟦{m[3]}⟧ du classement « {BOARD[m[4]]} » (tous les serveurs).{m[5] or ""}'
    m=re.fullmatch(r'(<p>)?Hold the #⟦(\d+)⟧ place of the board "(.+)" \(all servers\)\.(</p>)?',t)
    if m and m[3] in BOARD: return f'{m[1] or ""}Occupez la place n°⟦{m[2]}⟧ du classement « {BOARD[m[3]]} » (tous les serveurs).{m[4] or ""}'
    m=re.fullmatch(r'Guardian of rank (\w\+?) · level ⟦1⟧ · ⟦2⟧ HP\.',t)
    if m: return f'Gardien de rang {m[1]} · niveau ⟦1⟧ · ⟦2⟧ PV.'
    m=re.fullmatch(r'Guardian variant, rank (\w\+?)',t)
    if m: return f'Variante de gardien, rang {m[1]}'
    m=re.fullmatch(r'Floors ⟦1⟧ to ⟦2⟧: <strong>([A-Za-z ]+)</strong>( \(then the styles start over\))?',t)
    if m: return f'Étages ⟦1⟧ à ⟦2⟧ : <strong>{m[1]}</strong>'+(' (puis les styles recommencent)' if m[2] else '')
    m=re.fullmatch(r'<p><em>Note:</em> exclusive with ([a-z0-9-]+) \(classes with free branches take both\); each level past the first: \+⟦1⟧% power, -⟦2⟧% cooldown(; General tree: every class)?\.</p>',t)
    if m: return f'<p><em>Note :</em> exclusif avec {m[1]} (les classes à branches libres prennent les deux) ; chaque niveau après le premier : +⟦1⟧ % de puissance, -⟦2⟧ % de temps de recharge'+(' ; arbre général : toutes les classes' if m[2] else '')+'.</p>'
    m=re.fullmatch(r'<p><em>Note:</em> each level past the first: \+⟦1⟧% power, -⟦2⟧% cooldown(; General tree: every class)?\.</p>',t)
    if m: return '<p><em>Note :</em> chaque niveau après le premier : +⟦1⟧ % de puissance, -⟦2⟧ % de temps de recharge'+(' ; arbre général : toutes les classes' if m[1] else '')+'.</p>'
    m=re.fullmatch(r'Normal of rank (\w\+?) · level ⟦1⟧ · ⟦2⟧ HP\.',t)
    if m: return f'Normal de rang {m[1]} · niveau ⟦1⟧ · ⟦2⟧ PV.'
    m=re.fullmatch(r'<div><time>(October|November|December|September|January|February|March|April|May|June|July|August) ⟦1⟧ ⟦2⟧</time><span>·</span>⟦3⟧</div>',t)
    if m:
        mo={'October':'octobre','November':'novembre','December':'décembre','September':'septembre','January':'janvier','February':'février','March':'mars','April':'avril','May':'mai','June':'juin','July':'juillet','August':'août'}[m[1]]
        return f'<div><time>⟦1⟧ {mo} ⟦2⟧</time><span>·</span>⟦3⟧</div>'
    m=re.fullmatch(r'<p><em>Note:</em> (.+)\.</p>',t)
    if m:
        out=[]
        for part in m[1].split('; '):
            if part=='each level past the first: +⟦1⟧% power, -⟦2⟧% cooldown': out.append('chaque niveau après le premier : +⟦1⟧ % de puissance, -⟦2⟧ % de temps de recharge')
            elif part=='General tree: every class': out.append('arbre général : toutes les classes')
            elif part=='Mage school': out.append('école de mage')
            elif part=='human-only node (Human and Chad)': out.append('nœud réservé aux humains (Humain et Chad)')
            elif part.startswith('tree shared by: '): out.append('arbre partagé par : '+part[16:])
            else:
                q=re.fullmatch(r'exclusive with (.+) \(classes with free branches take both\)',part)
                if q: out.append(f'exclusif avec {q[1]} (les classes à branches libres prennent les deux)')
                else: return None
        return '<p><em>Note :</em> '+' ; '.join(out)+'.</p>'
    m=re.fullmatch(r'(<p>)?Reach level ⟦1⟧ as (Assassin|Attacker|Berserker|Bipolar|Chad|Mage|Necromancer|Overlord|Reaper|Support|Survivor|Tank|Warper)\.(</p>)?',t)
    if m: return f'{m[1] or ""}Atteignez le niveau ⟦1⟧ en tant que {m[2]}.{m[3] or ""}'
    m=re.fullmatch(r'(<p>)?Reach rank (A|B|C|D|E|S\+|S|Nation)\.(</p>)?',t)
    if m: return f'{m[1] or ""}Atteignez le rang {m[2]}.{m[3] or ""}'
    m=re.fullmatch(r'<span><span>Rank (A|B|C|D|E|S\+|S|Nation) dungeon</span></span>',t)
    if m: return f'<span><span>Donjon de rang {m[1]}</span></span>'
    m=re.fullmatch(r'rank (A|B|C|D|E|S\+|S|Nation) fallback guardian \(rift breaks\)',t)
    if m: return f'gardien de repli de rang {m[1]} (ruptures de faille)'
    m=re.fullmatch(r'rank (A|B|C|D|E|S\+|S|Nation) pool: city rift breaks( and roaming city monsters)?',t)
    if m: return f'réserve de rang {m[1]} : ruptures de faille en ville'+(' et monstres errants de la ville' if m[2] else '')
    m=re.fullmatch(r'Rank (A|B|C|D|E|S\+|S|Nation) to (A|B|C|D|E|S\+|S|Nation)',t)
    if m: return f'Rang {m[1]} vers {m[2]}'
    m=re.fullmatch(r'<p>Skill tree (⟦1⟧er|[A-Za-z]+), tier ⟦(\d)⟧: ⟦(\d)⟧ skill point per level, ⟦(\d)⟧ levels(.*)\.</p>',t)
    if m:
        tree=m[1]; rest=m[5]; parts=[x for x in rest.split('; ') if x]
        o=[]
        for x in parts:
            q=re.fullmatch(r'needs (.+?) maxed',x)
            q2=re.fullmatch(r'school costs ⟦(\d)⟧ school points for the Mage',x)
            if q: o.append('nécessite '+q[1].replace(' or ',' ou ')+' au maximum')
            elif q2: o.append(f"l'école coûte ⟦{q2[1]}⟧ points d'école pour le Mage")
            else: return None
        TR={'Arcane':'Arcane','Assassin':'Assassin','Attacker':'Attacker','Berserker':'Berserker','Binding':'Entrave','Duality':'Dualité','Earth':'Terre','Fire':'Feu','General':'Général','Ice':'Glace','Lightning':'Foudre','Necromancer':'Nécromancien','Overlord':'Overlord'}
        tn=TR.get(tree,tree)
        return f'<p>Arbre de compétences {tn}, palier ⟦{m[2]}⟧ : ⟦{m[3]}⟧ point de compétence par niveau, ⟦{m[4]}⟧ niveaux'+''.join(' ; '+x for x in o)+'.</p>'
    m=re.fullmatch(r'<p>weapon art of (item:[a-z0-9-]+) \(key E while it is held\)\.</p>',t)
    if m: return f"<p>art d'arme de {m[1]} (touche E tant qu'elle est tenue).</p>"
    m=re.fullmatch(r'<div><span>Update</span><span>·</span><time>(Nov|Oct|Sep|Dec|Aug|Jul|Jun|May|Apr|Mar|Feb|Jan) ⟦1⟧ ⟦2⟧</time><span>·</span><span>Overrank</span></div>',t)
    if m:
        mo={'Nov':'nov.','Oct':'oct.','Sep':'sept.','Dec':'déc.','Aug':'août','Jul':'juil.','Jun':'juin','May':'mai','Apr':'avr.','Mar':'mars','Feb':'févr.','Jan':'janv.'}[m[1]]
        return f'<div><span>Mise à jour</span><span>·</span><time>⟦1⟧ {mo} ⟦2⟧</time><span>·</span><span>Overrank</span></div>'
    m=re.fullmatch(r'tutorial starter gear \((.+)\)',t)
    if m:
        c={'assassin':'assassin','attacker':'attacker','human':'humain','mage':'mage','necromancer':'nécromancien','support':'support','tank':'tank'}
        parts=[x.strip() for x in m[1].split(',')]
        if all(x in c for x in parts): return 'équipement de départ du tutoriel ('+', '.join(c[x] for x in parts)+')'
    m=re.fullmatch(r'traveling merchant \(elixir offers, Rare and up; from rank (\w)\)',t)
    if m: return f"marchand itinérant (offres d'élixirs, Rare et plus ; à partir du rang {m[1]})"
    return None

EXACT={'Abilities':'Capacités','Action':'Action','Agility':'Agilité','Alcoves':'Alcôves','All':'Tout','All stats':'Toutes les stats','Also in the guides':'Aussi dans les guides','Arcane':'Arcane','Armor':'Armure','armor':'armure','Armor Gem':'Gemme d’armure','Assassin':'Assassin','Aspect':'Aspect','any':'tous','armor, pendant':'armure, pendentif','About badges':'À propos des badges','About titles':'À propos des titres','Accessories':'Accessoires','Accessory':'Accessoire','Armor and accessories':'Armures et accessoires','Anchor discount':'Réduction d’ancre','Anchor speed':'Vitesse d’ancre','At each grade':'À chaque grade','Ascension':'Ascension','A price chart per item':'Un graphique de prix par objet','A PvP ring':'Un ring PvP','Another awakened claims this rift.':'Un autre éveillé revendique ce rift.','A guardian test':'Un test de gardien'}
def exact(t):
    plain=re.sub(r'<[^>]+>','',t).strip()
    if plain in EXACT:
        return t.replace(plain,EXACT[plain])
    return None
_old_auto=auto
def auto(t):
    for f in (statline,cosm):
        r=f(re.sub(r'<[^>]+>','',t)) if f is statline and '<' not in t else (f(t) if '<' not in t else None)
        if r: return r
    for f in (item_sentence,misc,misc2):
        r=f(t)
        if r: return r
    r=exact(t)
    if r: return r
    return _old_auto(t)

def leftovers(t):
    s=auto(t) or t
    return [w for w in re.findall(r'(?<![\w’])[a-z]{3,}',clean(s)) if w in set(re.findall(r'[a-z]{3,}',clean(t))) and w not in OK_WORDS]
