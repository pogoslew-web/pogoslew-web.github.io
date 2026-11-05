"""Traduction française (revue manuelle) du texte rédactionnel des pages de classes.
Chaque bloc est traduit par remplacement de phrases dans le HTML d'origine : balises et liens restent intacts.
Les noms du jeu (classes, compétences, objets) ne sont pas traduits."""
import json,glob,os,re
R="/home/claude/overrank"
W={"Damage":"Dégâts"}
NOUN={"critical damage":"dégâts critiques","attack speed":"vitesse d’attaque","max mana":"mana max","mana regeneration":"régénération de mana","critical chance":"chance critique","evasion":"esquive","physical damage":"dégâts physiques","max HP":"PV max","damage reduction":"réduction de dégâts","damage":"dégâts","undead power":"puissance des morts-vivants","heals and boosts":"soins et boosts","boost duration":"durée des boosts","of max HP per second":"des PV max par seconde"}
def passive(h):
    def rep(m):
        t=m.group(0)
        for k in sorted(NOUN,key=len,reverse=True): t=t.replace(k,NOUN[k])
        return t
    h=re.sub(r"(?<=: )[^<]*",lambda m:rep(m).replace(" per level (up to "," par niveau (jusqu’à ").replace("%",""+" %"),h)
    return h
EXACT={
"<p>Every awakened starts as a <strong>Human</strong>: no class, a bit of everything. You can come back to it from the class window at any time.</p>":"<p>Tout éveillé commence <strong>Human</strong> : sans classe, un peu de tout. Vous pouvez y revenir à tout moment depuis la fenêtre de classe.</p>",
"<p>An assassin, plain and simple: fast moves and very high damage.</p>":"<p>Un assassin, tout simplement : mouvements rapides et dégâts très élevés.</p>",
"<p><strong>For you if:</strong> you like to appear, hit very hard and vanish.</p>":"<p><strong>Pour vous si :</strong> vous aimez surgir, frapper très fort et disparaître.</p>",
"<p>The sword's master: powerful blade arts, sturdy in the fray.</p>":"<p>Le maître de l’épée : de puissants arts de la lame, solide dans la mêlée.</p>",
"<p><strong>For you if:</strong> you want to charge into the fray, sword in hand.</p>":"<p><strong>Pour vous si :</strong> vous voulez foncer dans la mêlée, l’épée à la main.</p>",
"<p>Unawakened. No edge in skills, a bit more of everything else: stats, experience, and the whole General tree open.</p>":"<p>Non éveillé. Aucun avantage en compétences, un peu plus de tout le reste : stats, expérience, et tout l’arbre General ouvert.</p>",
"<p><strong>For you if:</strong> you want to try everything before choosing.</p>":"<p><strong>Pour vous si :</strong> vous voulez tout essayer avant de choisir.</p>",
"<p>Strikes from afar with the schools of magic, picked with school points (the rarest schools cost more).</p>":"<p>Frappe de loin avec les écoles de magie, choisies avec des points d’école (les écoles les plus rares coûtent plus cher).</p>",
"<p><strong>For you if:</strong> you prefer to strike from afar and pick your powers.</p>":"<p><strong>Pour vous si :</strong> vous préférez frapper de loin et choisir vos pouvoirs.</p>",
"<p>Undead fight at his side, always: more of them and stronger with more mana. In a dungeon he raises the monsters he defeats (they fade when he leaves).</p>":"<p>Les morts-vivants combattent à ses côtés, toujours : plus nombreux et plus forts avec plus de mana. En donjon, il relève les monstres qu’il vainc (ils disparaissent quand il part).</p>",
"<p><strong>For you if:</strong> you want undead fighting for you.</p>":"<p><strong>Pour vous si :</strong> vous voulez des morts-vivants qui se battent pour vous.</p>",
"<p>Heals and boosts: more damage and regeneration for the whole party.</p>":"<p>Soigne et booste : plus de dégâts et de régénération pour tout le groupe.</p>",
"<p><strong>For you if:</strong> you like your party to win thanks to you.</p>":"<p><strong>Pour vous si :</strong> vous aimez que votre groupe gagne grâce à vous.</p>",
"<p>Draws the monsters to him and holds the line: taunts, walls and a thick hide.</p>":"<p>Attire les monstres vers lui et tient la ligne : provocations, murs et peau épaisse.</p>",
"<p><strong>For you if:</strong> you want to take the hits for the others.</p>":"<p><strong>Pour vous si :</strong> vous voulez encaisser les coups pour les autres.</p>",
"<p>Pick it freely in the class window (status window, then <strong>Change class</strong>).</p>":"<p>Choisissez-la librement dans la fenêtre de classe (fenêtre de statut, puis <strong>Change class</strong>).</p>",
"<p>Changing class: the first change of a profile is free, then it costs <strong>100 shards × your level</strong> (at least 1,000). There is a 60 s delay between two changes, your level is kept by steps of 50 (level 449 becomes 400), and your stat points and skill trees are given back. See <a href=\"/en/w/overrank/formulas/economy\">Economy formulas</a>.</p>":"<p>Changer de classe : le premier changement d’un profil est gratuit, ensuite il coûte <strong>100 éclats × votre niveau</strong> (au moins 1 000). Il y a 60 s d’attente entre deux changements, votre niveau est conservé par paliers de 50 (le niveau 449 devient 400), et vos points de stats et arbres de compétences vous sont rendus. Voir les <a href=\"/en/w/overrank/formulas/economy\">formules d’économie</a>.</p>",
"<blockquote> <p><strong>Undiscovered class.</strong> The game keeps this class secret: its unlock condition shows as <code>???</code> and nobody has completed this page yet. Be the first to find out, then <strong>edit this page</strong> and tell everyone.</p> </blockquote>":"<blockquote> <p><strong>Classe non découverte.</strong> Le jeu garde cette classe secrète : sa condition de déblocage s’affiche <code>???</code> et personne n’a encore complété cette page. Soyez le premier à la découvrir, puis <strong>modifiez cette page</strong> et dites-le à tout le monde.</p> </blockquote>",
"<p>Some say a hunter who follows the whisper above is on the right track. <strong>Conditions unknown - discover them and edit this page.</strong></p>":"<p>On dit qu’un chasseur qui suit le murmure ci-dessus est sur la bonne voie. <strong>Conditions inconnues – découvrez-les et modifiez cette page.</strong></p>",
"<ul> <li>Explain how you unlocked it (keep it short and precise).</li> <li>Fill the stats, the weapons and the armor of the class.</li> <li>Describe its playstyle and its best builds.</li> <li>Remove the <em>Undiscovered</em> tag once the page is complete.</li> </ul>":"<ul> <li>Expliquez comment vous l’avez débloquée (court et précis).</li> <li>Remplissez les stats, les armes et l’armure de la classe.</li> <li>Décrivez son style de jeu et ses meilleurs builds.</li> <li>Retirez l’étiquette <em>Non découverte</em> une fois la page complète.</li> </ul>",
"<ul> <li>Fill the stats, the weapons and the armor of the class.</li> <li>Describe its playstyle and its best builds.</li> <li>Remove the <em>Undiscovered</em> tag once the page is complete.</li> </ul>":"<ul> <li>Remplissez les stats, les armes et l’armure de la classe.</li> <li>Décrivez son style de jeu et ses meilleurs builds.</li> <li>Retirez l’étiquette <em>Non découverte</em> une fois la page complète.</li> </ul>",
"<ul> <li>Fill the stats, the weapons and the armor of the class.</li> <li>Explain its skills</li> </ul>":"<ul> <li>Remplissez les stats, les armes et l’armure de la classe.</li> <li>Expliquez ses compétences.</li> </ul>",
"<p>Other secrets: see the <a href=\"/en/w/overrank/classes\">other special classes</a> and the <a href=\"/en/w/overrank/glossary/special-class\">glossary</a>.</p>":"<p>Autres secrets : voir les <a href=\"/en/w/overrank/classes\">autres classes spéciales</a> et le <a href=\"/en/w/overrank/glossary/special-class\">glossaire</a>.</p>",
"<p>Have all your stat points in intelligence, and that only. Has to be over 105 points.</p>":"<p>Mettre tous vos points de stats en intelligence, et rien d’autre. Il faut dépasser 105 points.</p>",
"<p>Solo, no-hit, clear multiple dungeons of your same rank or above as a human (2-5)</p>":"<p>En solo, sans prendre un seul coup, terminer plusieurs donjons de votre rang ou plus haut en tant qu’humain (2 à 5).</p>",
"<p>As a reaper you want to take advantage of the lifesteal, therefore glueing yourself to the enemies to keep a constant heal going is the common way of playing reaper.</p>":"<p>En tant que reaper, vous voulez profiter du vol de vie : se coller aux ennemis pour garder un soin constant est donc la façon habituelle de jouer reaper.</p>",
"<p>Once you are a high level reaper its reccomended to put enough points in perception to keep 75% critical and have enough agility to keep a 60% evasion, then put the rest of the points into strength.</p>":"<p>Une fois reaper de haut niveau, il est recommandé de mettre assez de points en perception pour garder 75 % de critique et assez d’agilité pour garder 60 % d’esquive, puis de mettre le reste des points en force.</p>",
"<p>Some users have experimented using SP and EX rank staffs to avoid the class debuff and play as a reaper-mage.</p>":"<p>Certains joueurs ont expérimenté des bâtons de rang SP et EX pour éviter le malus de classe et jouer reaper-mage.</p>",
"<p>Level 500 milestone reward for reaper (stars not included)</p>":"<p>Récompense de palier niveau 500 pour reaper (étoiles non incluses)</p>",
"<p>Your <strong>class</strong> decides your bonuses, your weapons, your armor, your skill tree and your playstyle. Everybody starts as a <strong>Human</strong> (no class). You can change class from the status window: the first change of a profile is free, later ones cost shards.</p>":"<p>Votre <strong>classe</strong> détermine vos bonus, vos armes, votre armure, votre arbre de compétences et votre style de jeu. Tout le monde commence <strong>Human</strong> (sans classe). Vous pouvez changer de classe depuis la fenêtre de statut : le premier changement d’un profil est gratuit, les suivants coûtent des éclats.</p>",
"<ul> <li><strong>Normal classes</strong> can be picked freely and stop at level 100.</li> <li><strong>Special classes</strong> are hidden: their unlock condition is a secret feat, and they go up to level 999.</li> <li>Each class has a <strong>role</strong> (damage, tank, support or hybrid) and a <strong>difficulty</strong> (easy, normal, hard).</li> </ul>":"<ul> <li>Les <strong>classes normales</strong> se choisissent librement et s’arrêtent au niveau 100.</li> <li>Les <strong>classes spéciales</strong> sont cachées : leur condition de déblocage est un exploit secret, et elles montent jusqu’au niveau 999.</li> <li>Chaque classe a un <strong>rôle</strong> (dégâts, tank, soutien ou hybride) et une <strong>difficulté</strong> (facile, normale, difficile).</li> </ul>",
"<p>Some special classes are <strong>undiscovered</strong>: their pages are blurred and ask for your help. If you find one, complete the page and remove the <em>Undiscovered</em> tag.</p>":"<p>Certaines classes spéciales sont <strong>non découvertes</strong> : leurs pages sont floutées et demandent votre aide. Si vous en trouvez une, complétez la page et retirez l’étiquette <em>Non découverte</em>.</p>",
"<p>The game gives a hint for each one in the class window. Players find the real conditions and write them here.</p>":"<p>Le jeu donne un indice pour chacune dans la fenêtre de classe. Les joueurs trouvent les vraies conditions et les écrivent ici.</p>",
"<p><em>Caps:</em> health bonus beyond +60% counts 50%; damage reduction capped at 65%.</p>":"<p><em>Plafonds :</em> le bonus de santé au-delà de +60 % ne compte que pour 50 % ; la réduction de dégâts est plafonnée à 65 %.</p>",
}
PHRASE=[("Last milestone reward for reaper","Dernière récompense de palier pour reaper"),("Note: Only the weapon from rewards is garuanteed to be your class.","Note : seule l’arme des récompenses est garantie d’être de votre classe.")]
DESC={"berserker":("A tank that hits harder when hurt","Un tank qui frappe plus fort quand il est blessé","Un bouclier tombé bien des fois... et qui a cessé de protéger qui que ce soit."),
"bipolar":("Area magic · fire and ice","Magie de zone · feu et glace","Un mage qui ne sait pas choisir entre brûler et geler."),
"chad":("No class · everything stronger","Sans classe · tout est plus fort","Certains humains n’ont jamais eu besoin d’une classe pour atteindre le sommet."),
"magic-attacker":("Sword and magic · melee","Épée et magie · mêlée","Certains attackers lisent plus de livres qu’ils ne fracassent de crânes."),
"overlord":("Summons · attack spells","Invocations · sorts d’attaque","Un nécromancien qui a tout misé sur son intelligence."),
"reaper":("Damage · steals life","Dégâts · vol de vie","Un simple humain, seul dans un donjon, intouchable."),
"survivor":("Damage · dodges · heals alone","Dégâts · esquive · se soigne seul","Un soutien qui se bat seul... et que rien ne touche jamais."),
"warper":("Mobility · strikes from rifts","Mobilité · frappes depuis les rifts","Un assassin dont l’intelligence est aussi tranchante que sa lame.")}
SUMMARY={"assassin":"Dégâts de mêlée · très mobile. Un assassin, tout simplement : mouvements rapides et dégâts très élevés.",
"attacker":"Dégâts de mêlée · robuste. Le maître de l’épée : de puissants arts de la lame, solide dans la mêlée.",
"human":"Sans classe · un peu de tout. Non éveillé. Aucun avantage en compétences, un peu plus de tout le reste : stats, expérience, et tout l’arbre General ouvert.",
"mage":"Magie à distance · choisit ses écoles. Frappe de loin avec les écoles de magie, choisies avec des points d’école (les écoles les plus rares coûtent plus cher).",
"necromancer":"Invocations · une armée à ses côtés. Les morts-vivants combattent à ses côtés, toujours : plus nombreux et plus forts avec plus de mana. En donjon, il relève les monstres qu’il vainc (ils disparaissent quand il part).",
"support":"Soins · renforce tout le groupe. Soigne et booste : plus de dégâts et de régénération pour tout le groupe.",
"tank":"Défense · protège le groupe. Attire les monstres vers lui et tient la ligne : provocations, murs et peau épaisse.",
"overview":"15 classes : l’Humain non éveillé, 6 classes à choisir librement et 8 classes spéciales à mériter."}
HEAD={"overview":"Présentation","playstyle":"Style de jeu","bonuses":"Bonus","equipment":"Équipement","skills":"Compétences","passives":"Passifs","how-to-unlock":"Comment débloquer","what-we-know":"Ce que l’on sait","stats-and-skills":"Stats et compétences","complete-this-page":"Compléter cette page","gear":"Équipement obtenu","class-card":"Fiche de classe","how-classes-work":"Comment fonctionnent les classes","picking-your-first-class":"Choisir sa première classe","roles":"Rôles","special-classes":"Classes spéciales"}
def equip(h):
    h=h.replace("Weapons:","Armes :").replace("Armor:","Armure :").replace("Stats to focus:","Stats à privilégier :").replace("Level cap:","Niveau max :").replace("</strong> any","</strong> toutes")
    return h
def whatweknow(slug):
    en,fr,wh=DESC[slug]
    return ("<ul> <li>C’est l’une des <strong>classes spéciales</strong> : on ne peut pas la choisir librement, il faut la mériter.</li> "
            f"<li>Dans la fenêtre de classe, elle est décrite ainsi : <em>{fr}</em>.</li> "
            f"<li>Le jeu murmure : <em>« {wh} »</em></li> "
            "<li>Comme toute classe spéciale, son niveau maximum est supérieur aux 100 des classes normales.</li> </ul>")
out_count=0
for f in sorted(glob.glob(R+"/db/entities/classes/*.json")):
    e=json.load(open(f)); slug=e["slug"]
    summ=SUMMARY.get(slug)
    if slug in DESC: summ="Une classe spéciale que personne n’a encore documentée. "+DESC[slug][1]+"."
    blocks={}; heads={}; missing=[]
    secs=[s for s in e["sections"] if s["blocks"] or s["heading"]]
    for i,s in enumerate(secs):
        key=s["id"] or f"#{i}"
        if s["id"] in HEAD and s["heading"]: heads[s["id"]]=HEAD[s["id"]]
        for j,b in enumerate(s["blocks"]):
            if b["type"] in("table","heading","model","image"): continue
            h=b.get("html","")
            fr=None
            if s["id"]=="what-we-know" and b["type"]=="ul": fr=whatweknow(slug)
            elif h in EXACT: fr=EXACT[h]
            elif s["id"]=="equipment" and "Weapons:" in h: fr=equip(h)
            elif s["id"]=="skills" and h.startswith("<p>Skills of the "):
                m=re.match(r"<p>Skills of the (.+?) tree\. Spend skill points to unlock and level them; each level past the first adds 15% power and removes 5% of the cooldown\.</p>",h)
                fr=f"<p>Compétences de l’arbre {m.group(1)}. Dépensez des points de compétence pour les débloquer et les monter de niveau ; chaque niveau après le premier ajoute 15 % de puissance et retire 5 % du temps de recharge.</p>" if m else None
            elif s["id"]=="passives": fr=passive(h)
            elif s["id"]=="gear":
                if "Last milestone reward" in h:
                    fr=h
                    for a,c in PHRASE: fr=fr.replace(a,c)
            if fr is None and b["type"] in("p","ul","ol","blockquote") and (b.get("text") or "").strip(): missing.append((key,j,b["text"][:60]))
            if fr is not None: blocks.setdefault(key,{})[str(j)]=fr
    d={"summary":summ,"headings":heads,"blocks":blocks}
    json.dump(d,open(f"{R}/db/i18n/fr/classes/{slug}.json","w"),ensure_ascii=False,indent=1)
    out_count+=1
    if missing: print(slug,"UNTRANSLATED:",missing)
print(out_count,"files")
