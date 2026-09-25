# -*- coding: utf-8 -*-
"""Turns research/design/prototyp.html into the live start page index.html:
+ FR/IT dictionaries, language menu in the sticky bar (4 languages), 'Wer nimmt Essen an' sheet,
  migration of the old page's localStorage (ub_state / ub_lang), links to app/, no 'Prototyp' wording."""
import re
SRC = '/home/user/uebrig/research/design/prototyp.html'
OUT = '/home/user/uebrig/index.html'
p = open(SRC, encoding='utf-8').read()

def rep(a, b, count=1):
    global p
    assert a in p, ('anchor missing: ' + a[:80])
    p = p.replace(a, b, count)

# ---------- head ----------
rep('<title>übrig – Prototyp</title>', '<title>übrig Bern – Freigabe, Etikett, Protokoll</title>')
rep('<meta name="description" content="Lokálny návrh Übrig po redesigne „Lístok a pečiať“: intro, koncept, lis, kruh, zatrasenie, záblesk, lístok, protokol. Nič sa neposiela – všetko ostáva v prehliadači.">',
    '<meta name="description" content="Was in der Küche übrig bleibt, sicher weitergeben: sieben Hygiene-Fragen, Meldung, Etikett, Protokoll. Ohne Konto, ohne Server – alles bleibt im Browser. Bern.">')

# ---------- language menu in sticky bar (4 languages) ----------
rep("""      <span class="langs" role="group" aria-label="Sprache / Language"><button type="button" data-lang="de" aria-pressed="true">DE</button><button type="button" data-lang="en" aria-pressed="false">EN</button></span>""",
    """      <span class="langmenu"><button type="button" class="langbtn" id="langBtn" aria-haspopup="listbox" aria-expanded="false" aria-label="Sprache">DE <span aria-hidden="true">▾</span></button>
        <div class="langs" id="langList" role="listbox" aria-label="Sprache / Langue / Lingua / Language" hidden><button type="button" role="option" data-lang="de" aria-pressed="true">Deutsch</button><button type="button" role="option" data-lang="fr" aria-pressed="false">Français</button><button type="button" role="option" data-lang="it" aria-pressed="false">Italiano</button><button type="button" role="option" data-lang="en" aria-pressed="false">English</button></div></span>""")
rep(""".langs{display:flex;gap:0;font-family:var(--f-fact);font-size:11px;letter-spacing:.1em;margin:0 2px}
.langs button{background:none;border:0;padding:0 6px;min-height:40px;min-width:32px;color:var(--mute);border-bottom:2px solid transparent;border-radius:0}
.langs button[aria-pressed=true]{color:var(--ink);border-bottom-color:var(--stamp)}""",
    """.langmenu{position:relative;margin:0 2px}
.langbtn{background:none;border:0;padding:0 6px;min-height:40px;font-family:var(--f-fact);font-size:11px;letter-spacing:.1em;color:var(--ink)}
.langs{position:absolute;top:100%;right:0;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:6px;display:grid;gap:2px;min-width:150px;box-shadow:4px 4px 0 var(--rule);z-index:35}
.langs button{background:none;border:0;text-align:left;padding:10px 12px;min-height:44px;color:var(--ink-2);border-radius:6px;font-size:14px}
.langs button[aria-pressed=true]{color:var(--ink);font-weight:700;background:var(--paper)}""")
rep("""  document.querySelectorAll('.langs button').forEach(function(b){b.addEventListener('click',function(){lang=b.dataset.lang;try{localStorage.setItem('uebrig-prototyp-lang',lang)}catch(e){}applyLang();render()})});""",
    """  document.querySelectorAll('.langs button').forEach(function(b){b.addEventListener('click',function(){lang=b.dataset.lang;try{localStorage.setItem('uebrig-lang',lang)}catch(e){}$('langList').hidden=true;$('langBtn').setAttribute('aria-expanded','false');applyLang();render()})});
  $('langBtn').addEventListener('click',function(e){e.stopPropagation();var l=$('langList');l.hidden=!l.hidden;this.setAttribute('aria-expanded',l.hidden?'false':'true')});
  document.addEventListener('click',function(e){var l=$('langList');if(!l.hidden&&!e.target.closest('.langmenu')){l.hidden=true;$('langBtn').setAttribute('aria-expanded','false')}});""")
rep("""    document.querySelectorAll('.langs button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.lang===lang?'true':'false')});""",
    """    document.querySelectorAll('.langs button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.lang===lang?'true':'false')});
    $('langBtn').firstChild.textContent=lang.toUpperCase()+' ';""")
rep("""  var lang='de';try{lang=localStorage.getItem('uebrig-prototyp-lang')||((navigator.language||'').slice(0,2)==='en'?'en':'de')}catch(e){}
  if(!I18N[lang])lang='de';""",
    """  var lang='de';try{lang=localStorage.getItem('uebrig-lang')||localStorage.getItem('uebrig-prototyp-lang')||localStorage.getItem('ub_lang')||(navigator.language||'de').slice(0,2).toLowerCase()}catch(e){}
  if(!I18N[lang])lang='de';""")

# ---------- storage keys + migration of the old page ----------
rep("""  var KEY='uebrig-prototyp-v2';""", """  var KEY='uebrig-v3';""")
rep("""  try{var raw=localStorage.getItem(KEY)||localStorage.getItem('uebrig-prototyp-v1');if(raw){""",
    """  try{var raw=localStorage.getItem(KEY)||localStorage.getItem('uebrig-prototyp-v2')||localStorage.getItem('uebrig-prototyp-v1');if(raw){""")
rep("""    if(state.fields.contact&&!state.fields.business){state.fields.business=state.fields.contact}}}catch(e){}""",
    """    if(state.fields.contact&&!state.fields.business){state.fields.business=state.fields.contact}}
    /* alte Startseite (ub_state): Protokoll und Betrieb übernehmen, wenn noch kein neues Protokoll existiert */
    var old=localStorage.getItem('ub_state');
    if(old&&!state.log.length){var o=JSON.parse(old);(o.log||[]).slice().reverse().forEach(function(e,i){state.log.push({id:'ub'+i,at:e.d||'',dish:e.dish||'',portions:String(e.qty||'').replace(/\\D+.*$/,''),window:'',place:e.to&&e.to!=='—'?e.to:'',business:o.biz||'',phone:'',email:'',allergens:[],cooked:'',best:'',legacy:true})});
      if(o.biz&&!state.fields.business)state.fields.business=o.biz;if(o.contact&&!state.fields.phone)state.fields.phone=o.contact}}catch(e){}""")
rep("""  var tips={};try{tips=JSON.parse(localStorage.getItem('uebrig-prototyp-tips')||'{}')||{}}catch(e){}
  var tipsOn=true;try{tipsOn=localStorage.getItem('uebrig-prototyp-tips-on')!=='0'}catch(e){}
  function saveTips(){try{localStorage.setItem('uebrig-prototyp-tips',JSON.stringify(tips));localStorage.setItem('uebrig-prototyp-tips-on',tipsOn?'1':'0')}catch(e){}}""",
    """  var tips={};try{tips=JSON.parse(localStorage.getItem('uebrig-tips')||localStorage.getItem('uebrig-prototyp-tips')||'{}')||{}}catch(e){}
  var tipsOn=true;try{tipsOn=(localStorage.getItem('uebrig-tips-on')||localStorage.getItem('uebrig-prototyp-tips-on'))!=='0'}catch(e){}
  function saveTips(){try{localStorage.setItem('uebrig-tips',JSON.stringify(tips));localStorage.setItem('uebrig-tips-on',tipsOn?'1':'0')}catch(e){}}""")

# ---------- footer / wording ----------
rep("""  <p class="foot no-print" data-i18n="foot">Prototyp · nichts verlässt den Browser · Logo tippen = Intro nochmals</p>""",
    """  <p class="foot no-print" data-i18n="foot">übrig Bern · nichts verlässt den Browser · Logo tippen = Intro nochmals</p>
  <p class="foot no-print"><a href="app/" data-i18n="app_link" style="color:var(--stamp)">Plattform: Angebote live melden und reservieren (Anmeldung)</a> · <a href="research/" style="color:var(--mute)">Research</a> · <a href="https://github.com/richardcervenka111-create/uebrig" rel="noopener" style="color:var(--mute)">GitHub</a></p>""")
rep("""    <div class="actions">
      <button class="press stamp" type="button" data-close="concept"><span class="shade"></span><span class="face" data-i18n="c_go">Los geht's</span></button>
      <button class="press ghost" type="button" data-open="support"><span class="shade"></span><span class="face" data-i18n="support">Unterstützen</span></button>
    </div>""",
    """    <div class="actions">
      <button class="press stamp" type="button" data-close="concept"><span class="shade"></span><span class="face" data-i18n="c_go">Los geht's</span></button>
      <button class="press ghost" type="button" data-open="orgs"><span class="shade"></span><span class="face" data-i18n="orgs_btn">Wer nimmt Essen an</span></button>
      <button class="press ghost" type="button" data-open="support"><span class="shade"></span><span class="face" data-i18n="support">Unterstützen</span></button>
    </div>""")

# ---------- 'Wer nimmt Essen an' sheet ----------
rep("""<!-- welcome after 7/7 -->""", """<!-- organisations that take food -->
<div class="veil" id="orgs" hidden role="dialog" aria-modal="true" aria-labelledby="o-title">
  <div class="sheetbox"><button type="button" class="x" data-close="orgs" aria-label="Schliessen">×</button>
    <span class="k" data-i18n="o_k">Abnehmer in Bern</span>
    <h2 id="o-title" data-i18n="o_title">Wer nimmt Essen an</h2>
    <p data-i18n="o_note">Startliste (Stand 25.9.2026). Vor der ersten Übergabe anrufen und Bedingungen klären; deine Notizen bleiben in diesem Browser.</p>
    <div class="steps" id="orgList"></div>
  </div>
</div>

<!-- welcome after 7/7 -->""")
rep("""    <div class="tip" data-tip="form"><span class="k">Info</span><span class="t"></span><button type="button" class="x" aria-label="Schliessen">×</button></div>""",
    """    <div class="tip" data-tip="form"><span class="k">Info</span><span class="t"></span><button type="button" class="x" aria-label="Schliessen">×</button></div>
    <div style="margin:0 0 14px"><button class="press ghost" type="button" data-open="orgs"><span class="shade"></span><span class="face" data-i18n="orgs_btn">Wer nimmt Essen an</span></button></div>""")
rep(""".stepc .n{font-family:var(--f-fact);color:var(--stamp);font-size:13px;padding-top:2px}""",
    """.stepc .n{font-family:var(--f-fact);color:var(--stamp);font-size:13px;padding-top:2px}
.org{display:grid;gap:6px;background:var(--paper);border:1px solid var(--rule);border-radius:var(--radius-card);padding:12px}
.org b{font-size:15px}.org small{color:var(--ink-2);display:block}.org .mono{font-size:12px;color:var(--mute)}
.org a{color:var(--stamp);font-weight:700;text-decoration:none}
.org textarea{min-height:44px;font-size:13px;padding:8px 10px}""")
# org data + render (after tips block)
rep("""  /* ---- language ---- */""", """  /* ---- organisations (Startliste; Angaben aus Snippets 25.9.2026 – bestätigen) ---- */
  var ORGS=[
    {id:'passantenheim',name:'Passantenheim Bern (Heilsarmee)',addr:'Muristrasse 6, 3006 Bern',tel:'031 351 80 27'},
    {id:'sleeper',name:'Sleeper – Notschlafstelle & Gassenküche',addr:'Neubrückstrasse 19, 3012 Bern',tel:'031 301 64 04'},
    {id:'punkt6',name:'Punkt 6 – Aufenthaltsraum PINTO (Stadt Bern)',addr:'Nägeligasse 3a, 3011 Bern',tel:'031 321 76 38'},
    {id:'pluto',name:'Pluto – Jugend-Notschlafstelle',addr:'Studerstrasse 44, 3004 Bern',tel:''},
    {id:'gassenkueche',name:'Gassenküche Bern (Kirchliche Gassenarbeit)',addr:'',tel:''},
    {id:'fairteiler',name:'foodsharing Bern – Fairteiler / Madame Frigo',addr:'',tel:''}
  ];
  var orgNotes={};try{orgNotes=JSON.parse(localStorage.getItem('uebrig-orgs')||'{}')||{}}catch(e){}
  function renderOrgs(){
    var box=$('orgList');box.textContent='';
    ORGS.forEach(function(o){
      var d=document.createElement('div');d.className='org';
      var b=document.createElement('b');b.textContent=o.name;d.appendChild(b);
      var s=document.createElement('small');s.textContent=T('orgs_desc')[o.id]||'';d.appendChild(s);
      if(o.addr){var a=document.createElement('span');a.className='mono';a.textContent=o.addr;d.appendChild(a)}
      if(o.tel){var t=document.createElement('a');t.href='tel:'+o.tel.replace(/\\s+/g,'');t.textContent=T('o_call')+' '+o.tel;d.appendChild(t)}
      var ta=document.createElement('textarea');ta.placeholder=T('o_notes');ta.value=orgNotes[o.id]||'';ta.setAttribute('aria-label',T('o_notes'));
      ta.addEventListener('input',function(){orgNotes[o.id]=ta.value;try{localStorage.setItem('uebrig-orgs',JSON.stringify(orgNotes))}catch(e){}});
      d.appendChild(ta);box.appendChild(d);
    });
  }

  /* ---- language ---- */""")
rep("""    applyTips();$('rmNote').textContent=T('rm');
  }""", """    applyTips();$('rmNote').textContent=T('rm');renderOrgs();
  }""")

# ---------- dictionaries: DE/EN additions, FR/IT new ----------
rep("""        d_edit:'Bearbeiten',d_label:'Etikett zeigen',d_del:'Eintrag löschen',d_confirm:'Diesen Eintrag löschen?',d_place:'Ort',d_contact:'Kontakt',d_window:'Abholen',d_all:'Allergene',d_cooked:'Zubereitet',d_best:'Konsumieren bis'},""",
    """        d_edit:'Bearbeiten',d_label:'Etikett zeigen',d_del:'Eintrag löschen',d_confirm:'Diesen Eintrag löschen?',d_place:'Ort',d_contact:'Kontakt',d_window:'Abholen',d_all:'Allergene',d_cooked:'Zubereitet',d_best:'Konsumieren bis',
        orgs_btn:'Wer nimmt Essen an',o_k:'Abnehmer in Bern',o_title:'Wer nimmt Essen an',o_note:'Startliste (Stand 25.9.2026). Vor der ersten Übergabe anrufen und Bedingungen klären; deine Notizen bleiben in diesem Browser.',o_call:'Anrufen',o_notes:'Meine Notizen (Ansprechperson, Bedingungen, Zeiten)',
        orgs_desc:{passantenheim:'Notschlafstelle mit Halbpension, 50–60 Betten. Eintritt bis 23:00 – geeignet für späte Küchen.',sleeper:'20 Betten, kocht selbst (Schweizer Tafel). Abendessen 18–20 Uhr; gekühlte Ware für den nächsten Tag anfragen.',punkt6:'Winter 18:00–22:30, bisher Kaffee und Sandwiches. Ob warme Speisen erlaubt sind: nachfragen.',pluto:'Jugendliche 14–23, 7 Betten, 18:00–09:00, warmes Abendessen. Kleine Mengen.',gassenkueche:'Mahlzeiten für CHF 5, seit 1984. Adresse und Zeiten vor Ort klären.',fairteiler:'Öffentliche Kühlschränke, ohne Aufsicht. Nur nach den Regeln des jeweiligen Fairteilers – gekochte Speisen meist nicht.'},
        app_link:'Plattform: Angebote live melden und reservieren (Anmeldung)'},""")
rep("""        d_edit:'Edit',d_label:'Show label',d_del:'Delete entry',d_confirm:'Delete this entry?',d_place:'Place',d_contact:'Contact',d_window:'Pick up',d_all:'Allergens',d_cooked:'Prepared',d_best:'Consume by'}
  };""",
    """        d_edit:'Edit',d_label:'Show label',d_del:'Delete entry',d_confirm:'Delete this entry?',d_place:'Place',d_contact:'Contact',d_window:'Pick up',d_all:'Allergens',d_cooked:'Prepared',d_best:'Consume by',
        orgs_btn:'Who accepts food',o_k:'Receivers in Bern',o_title:'Who accepts food',o_note:'Starter list (as of 25 Sept 2026). Call before the first hand-over and agree the conditions; your notes stay in this browser.',o_call:'Call',o_notes:'My notes (contact person, conditions, times)',
        orgs_desc:{passantenheim:'Night shelter with half board, 50–60 beds. Entry until 23:00 – suits late kitchens.',sleeper:'20 beds, cooks itself (Schweizer Tafel). Dinner 18–20; ask about chilled food for the next day.',punkt6:'Winter 18:00–22:30, so far coffee and sandwiches. Ask whether hot dishes are allowed.',pluto:'Youth 14–23, 7 beds, 18:00–09:00, warm dinner. Small quantities.',gassenkueche:'Meals for CHF 5, since 1984. Clarify address and times on site.',fairteiler:'Public fridges, unattended. Only by the rules of each Fairteiler – cooked dishes usually not.'},
        app_link:'Platform: post and reserve offers live (sign-in)'},
    fr:{tab_check:'Vérifier',tab_form:'Annonce',tab_ticket:'Étiquette',tab_log:'Journal',
        step:{check:'1  Vérifier',form:'2  Annonce',ticket:'3  Étiquette',log:'4  Journal'},
        rules:["Pas de l’espace clients","Chaud ≥ 65 °C ou ≤ 5 °C","L’heure sur l’étiquette","14 allergènes connus","Récipient fermé","Chaîne du froid / caisson chaud","Le receveur connaît le délai"],
        why:["Seulement des plats qui n’ont jamais été dans l’espace clients : cuisine, passe, réserve du buffet. Ce qui était sur une table ne repart pas.",
             "Maintenu chaud au-dessus de 65 °C – ou refroidi à 5 °C ou moins en deux heures. Entre les deux, les germes se multiplient.",
             "Préparé quand, à consommer jusqu’à quand : les deux vont sur l’étiquette. Sans heures, le receveur ne peut rien décider.",
             "Tu sais lesquels des 14 allergènes à déclarer ce plat contient – et tu les notes.",
             "Couvercle fermé, propre, pas à l’air libre dans un bac. Le récipient voyage ; il revient ou il reste.",
             "En route, ça reste froid (glacière) ou chaud (caisson chaud). Pas de coffre de voiture sans caisson.",
             "L’organisation sait jusqu’à quand elle doit servir ou jeter – c’est sur l’étiquette et dans l’annonce."],
        allergens:["Gluten","Crustacés","Œufs","Poissons","Arachides","Soja","Lait","Fruits à coque","Céleri","Moutarde","Sésame","Sulfites","Lupin","Mollusques"],
        note_check:'Sept questions. Toutes oui — sinon rien ne sort. Le i explique chaque ligne.',
        f_dish:'Plat',ph_dish:'p. ex. risotto aux légumes, salade à part',f_portions:'Portions',f_state:'État',st_cold:'réfrigéré',st_hot:'chaud',
        f_from:'À retirer dès',f_until:'jusqu’à',f_place:'Lieu',ph_place:'Rue, entrée',f_business:'Établissement',ph_business:'Restaurant Sonne',f_phone:'Téléphone',f_email:'E-mail',f_allergens:'Allergènes',f_cooked:'Préparé',f_best:'À consommer jusqu’au',
        confirm:'Allergènes et « à consommer jusqu’au » sont vérifiés et corrects.',confirm_hint:'Merci de confirmer – sans cela, pas d’étiquette.',
        reheat:'Bien réchauffer avant de servir.',note_ticket:'La même forme va sur WhatsApp et sur le récipient.',print:'Imprimer l’étiquette',foot:'übrig Berne · rien ne quitte le navigateur · toucher le logo = revoir l’intro',
        left:function(n){return 'Encore '+n+' sur 7'},hint_check:function(n){return 'Encore '+n+' sur 7 — celle-ci d’abord.'},next_form:'Vers l’annonce',show_ticket:'Voir l’étiquette',to_log:'Mettre au journal',save_edit:'Enregistrer la modification',new_check:'Nouvelle libération',
        missing:'Manque encore.',bad_email:'Cela ne ressemble pas à un e-mail.',without:function(f){return 'Sans '+f+', pas d’étiquette.'},portions:'portions',port:'port.',allerg:'Allergènes',cooked:'Préparé',best:'À consommer jusqu’au',pickup:'Retrait',none:'aucun indiqué',empty:'Pas encore d’entrée. Local, dans le navigateur.',edited:'modifié',
        state:{'gekühlt':'réfrigéré','heiss':'chaud'},
        tips:{check:'Sept questions d’hygiène. Touche chacune qui est vraie ; le i à côté l’explique. À 7 sur 7 seulement, le bouton en bas devient rouge et on continue.',
              form:'Quoi, combien, quand, où – et qui. Plat, portions, lieu, établissement et téléphone sont obligatoires ; tout en bas, tu confirmes allergènes et délai.',
              ticket:'Voici l’étiquette. Imprimer (une page) ou copier le texte ci-dessous dans WhatsApp. « Mettre au journal » enregistre la remise.',
              log:'Le journal reste uniquement dans ce navigateur. Touche une entrée : voir, modifier, revoir l’étiquette ou supprimer.'},
        info_close:'Fermer',info_btn:'Conseils on/off',rm:'Mouvement réduit : ton appareil a « Réduire les animations » activé – les animations sont donc désactivées.',enter:'Entrer',support:'Soutenir',close:'Fermer',
        c_k:'Le concept',c_title:'Ce qui reste en cuisine repart en sécurité.',
        c_p1:'übrig est le bout de papier des quinze dernières minutes du service : sept questions d’hygiène, une annonce, une étiquette, un journal. Ce qui est libéré est retiré par une organisation sociale – le soir même.',
        c_s1:'Vérifier',c_s1t:'Sept questions. Toutes oui, sinon rien ne sort.',c_s2:'Annonce',c_s2t:'Quoi, combien, quand, où – et qui remet.',c_s3:'Étiquette',c_s3t:'Sur le récipient et dans le groupe. Même forme, même ordre.',c_s4:'Journal',c_s4t:'Reste dans le navigateur. Les deux côtés savent ce qui a été remis, et quand.',
        c_p2:'Pas de compte, pas de serveur, pas de tableau de bord. Construit à Berne par des bénévoles – pour les cuisines et pour les personnes qui ont encore besoin d’un plat chaud le soir.',c_go:'C’est parti',
        s_k:'Soutenir',s_title:'Une soirée übrig coûte onze francs.',s_p1:'C’est le prix d’un vélo-cargo électrique pour une tournée (carvelo2go, trois heures). Caissons isothermes, étiquettes, coordination – l’association porte tout. Pas d’investisseur, pas de publicité.',
        s_p2:'Trois façons d’aider : participer comme cuisine, retirer comme organisation, ou contribuer. Le compte de dons suivra la fondation de l’association – d’ici là, chaque contact compte.',s_share:'Partager le lien',share_ok:'Lien copié.',share_fail:'Copie impossible – copier l’adresse en haut du navigateur.',
        w_k:'Sept fois oui',w_title:'Libéré.',w_p:'Le plat peut sortir. Encore trois choses : ce que c’est, combien, et quand on peut le retirer. Puis tu imprimes l’étiquette.',w_go:'Vers l’annonce',
        d_edit:'Modifier',d_label:'Voir l’étiquette',d_del:'Supprimer l’entrée',d_confirm:'Supprimer cette entrée ?',d_place:'Lieu',d_contact:'Contact',d_window:'Retrait',d_all:'Allergènes',d_cooked:'Préparé',d_best:'À consommer jusqu’au',
        orgs_btn:'Qui accepte de la nourriture',o_k:'Receveurs à Berne',o_title:'Qui accepte de la nourriture',o_note:'Liste de départ (état au 25.9.2026). Appeler avant la première remise et clarifier les conditions ; tes notes restent dans ce navigateur.',o_call:'Appeler',o_notes:'Mes notes (personne de contact, conditions, horaires)',
        orgs_desc:{passantenheim:'Hébergement d’urgence en demi-pension, 50–60 lits. Entrée jusqu’à 23h – convient aux cuisines tardives.',sleeper:'20 lits, cuisine elle-même (Table Suisse). Repas 18–20h ; demander pour des denrées réfrigérées pour le lendemain.',punkt6:'Hiver 18h–22h30, jusqu’ici café et sandwiches. Demander si les plats chauds sont admis.',pluto:'Jeunes 14–23 ans, 7 lits, 18h–9h, repas chaud le soir. Petites quantités.',gassenkueche:'Repas à CHF 5, depuis 1984. Adresse et horaires à clarifier sur place.',fairteiler:'Frigos publics, sans surveillance. Uniquement selon les règles de chaque Fairteiler – plats cuisinés en général non.'},
        app_link:'Plateforme : annoncer et réserver des offres en direct (connexion)'},
    it:{tab_check:'Verifica',tab_form:'Annuncio',tab_ticket:'Etichetta',tab_log:'Registro',
        step:{check:'1  Verifica',form:'2  Annuncio',ticket:'3  Etichetta',log:'4  Registro'},
        rules:["Non dalla zona ospiti","Caldo ≥ 65 °C o ≤ 5 °C","L’ora sull’etichetta","14 allergeni noti","Contenitore chiuso","Catena del freddo / box termico","Chi riceve conosce la scadenza"],
        why:["Solo cibo che non è mai stato nella zona ospiti: cucina, pass, scorta del buffet. Ciò che era su un tavolo non prosegue.",
             "Tenuto caldo sopra i 65 °C – oppure raffreddato a 5 °C o meno entro due ore. Nel mezzo i germi crescono.",
             "Preparato quando, da consumare entro quando: entrambi vanno sull’etichetta. Senza orari chi riceve non può decidere.",
             "Sai quali dei 14 allergeni da dichiarare contiene questo piatto – e li scrivi.",
             "Coperchio chiuso, pulito, non aperto in una teglia. Il contenitore viaggia; torna o resta.",
             "Lungo il tragitto resta freddo (borsa frigo) o caldo (box termico). Niente bagagliaio senza box.",
             "L’organizzazione sa entro quando deve servire o smaltire – è sull’etichetta e nell’annuncio."],
        allergens:["Glutine","Crostacei","Uova","Pesce","Arachidi","Soia","Latte","Frutta a guscio","Sedano","Senape","Sesamo","Solfiti","Lupini","Molluschi"],
        note_check:'Sette domande. Tutte sì — altrimenti non esce nulla. La i spiega ogni riga.',
        f_dish:'Piatto',ph_dish:'es. risotto alle verdure, insalata a parte',f_portions:'Porzioni',f_state:'Stato',st_cold:'refrigerato',st_hot:'caldo',
        f_from:'Ritiro dalle',f_until:'alle',f_place:'Luogo',ph_place:'Via, ingresso',f_business:'Esercizio',ph_business:'Restaurant Sonne',f_phone:'Telefono',f_email:'E-mail',f_allergens:'Allergeni',f_cooked:'Preparato',f_best:'Consumare entro',
        confirm:'Allergeni e «consumare entro» sono verificati e corretti.',confirm_hint:'Conferma per favore – senza, niente etichetta.',
        reheat:'Riscaldare bene prima di servire.',note_ticket:'La stessa forma va su WhatsApp e sul contenitore.',print:'Stampa etichetta',foot:'übrig Berna · nulla lascia il browser · tocca il logo = intro di nuovo',
        left:function(n){return 'Ancora '+n+' su 7'},hint_check:function(n){return 'Ancora '+n+' su 7 — prima questa.'},next_form:'Avanti all’annuncio',show_ticket:'Mostra etichetta',to_log:'Metti nel registro',save_edit:'Salva modifica',new_check:'Nuova liberatoria',
        missing:'Manca ancora.',bad_email:'Non sembra un’e-mail.',without:function(f){return 'Senza '+f+' niente etichetta.'},portions:'porzioni',port:'porz.',allerg:'Allergeni',cooked:'Preparato',best:'Consumare entro',pickup:'Ritiro',none:'nessuno indicato',empty:'Ancora nessuna voce. Locale, nel browser.',edited:'modificato',
        state:{'gekühlt':'refrigerato','heiss':'caldo'},
        tips:{check:'Sette domande d’igiene. Tocca ogni riga che è vera; la i accanto la spiega. Solo a 7 su 7 il pulsante in basso diventa rosso e si prosegue.',
              form:'Cosa, quanto, quando, dove – e chi. Piatto, porzioni, luogo, esercizio e telefono sono obbligatori; in fondo confermi allergeni e scadenza.',
              ticket:'Ecco l’etichetta. Stampala (una pagina) o copia il testo qui sotto in WhatsApp. «Metti nel registro» registra la consegna.',
              log:'Il registro resta solo in questo browser. Tocca una voce: vedere, modificare, rivedere l’etichetta o eliminare.'},
        info_close:'Chiudi',info_btn:'Suggerimenti on/off',rm:'Movimento ridotto: il tuo dispositivo ha «Riduci movimento» attivo – le animazioni sono quindi disattivate.',enter:'Entra',support:'Sostieni',close:'Chiudi',
        c_k:'Il concetto',c_title:'Ciò che resta in cucina prosegue in sicurezza.',
        c_p1:'übrig è il foglietto degli ultimi quindici minuti del turno: sette domande d’igiene, un annuncio, un’etichetta, un registro. Ciò che è liberato viene ritirato da un’organizzazione sociale – la sera stessa.',
        c_s1:'Verifica',c_s1t:'Sette domande. Tutte sì, altrimenti non esce nulla.',c_s2:'Annuncio',c_s2t:'Cosa, quanto, quando, dove – e chi consegna.',c_s3:'Etichetta',c_s3t:'Sul contenitore e nel gruppo. Stessa forma, stesso ordine.',c_s4:'Registro',c_s4t:'Resta nel browser. Entrambe le parti sanno cosa è stato consegnato e quando.',
        c_p2:'Nessun account, nessun server, nessuna dashboard. Costruito a Berna da volontari – per le cucine e per le persone che la sera hanno ancora bisogno di qualcosa di caldo.',c_go:'Si parte',
        s_k:'Sostieni',s_title:'Una sera di übrig costa undici franchi.',s_p1:'Tanto costa una e-cargo bike per un giro di ritiro (carvelo2go, tre ore). Box termici, etichette, coordinamento – tutto a carico dell’associazione. Nessun investitore, nessuna pubblicità.',
        s_p2:'Tre modi per aiutare: partecipare come cucina, ritirare come organizzazione, o contribuire. Il conto per le donazioni arriva con la fondazione dell’associazione – fino ad allora conta ogni contatto.',s_share:'Condividi il link',share_ok:'Link copiato.',share_fail:'Copia non riuscita – copia l’indirizzo in alto nel browser.',
        w_k:'Sette volte sì',w_title:'Liberato.',w_p:'Il cibo può uscire. Ancora tre cose: cos’è, quanto, e quando si può ritirare. Poi stampi l’etichetta.',w_go:'All’annuncio',
        d_edit:'Modifica',d_label:'Mostra etichetta',d_del:'Elimina voce',d_confirm:'Eliminare questa voce?',d_place:'Luogo',d_contact:'Contatto',d_window:'Ritiro',d_all:'Allergeni',d_cooked:'Preparato',d_best:'Consumare entro',
        orgs_btn:'Chi accetta cibo',o_k:'Riceventi a Berna',o_title:'Chi accetta cibo',o_note:'Elenco iniziale (stato 25.9.2026). Chiamare prima della prima consegna e chiarire le condizioni; le tue note restano in questo browser.',o_call:'Chiama',o_notes:'Le mie note (referente, condizioni, orari)',
        orgs_desc:{passantenheim:'Alloggio d’emergenza con mezza pensione, 50–60 letti. Ingresso fino alle 23 – adatto a cucine tardive.',sleeper:'20 letti, cucina in proprio (Tavola Svizzera). Cena 18–20; chiedere per merce refrigerata per il giorno dopo.',punkt6:'Inverno 18:00–22:30, finora caffè e panini. Chiedere se i piatti caldi sono ammessi.',pluto:'Giovani 14–23, 7 letti, 18:00–09:00, cena calda. Piccole quantità.',gassenkueche:'Pasti a CHF 5, dal 1984. Indirizzo e orari da chiarire sul posto.',fairteiler:'Frigoriferi pubblici, senza sorveglianza. Solo secondo le regole del singolo Fairteiler – piatti cucinati di norma no.'},
        app_link:'Piattaforma: annunciare e prenotare offerte in diretta (accesso)'}
  };""")

open(OUT, 'w', encoding='utf-8').write(p)
# checks mirroring the Pages workflow
import subprocess
print('viewport', 'name="viewport"' in p, '| data-lang count', p.count('data-lang='), '| network calls', bool(re.search(r'fetch\(|XMLHttpRequest|sendBeacon', p, re.I)))
# key parity across languages
def keys(block):
    return set(re.findall(r"(?<![\w'])(\w+):(?=['\"\[{f])", block))
i = p.index('var I18N={'); j = p.index('  };', i)
dic = p[i:j]
parts = {L: dic[dic.index('\n    ' + L + ':{'):] for L in ['de', 'en', 'fr', 'it']}
for L in ['en', 'fr', 'it']:
    seg = parts[L].split('\n    it:{')[0] if L != 'it' else parts[L]
    seg = seg.split('\n    fr:{')[0] if L == 'en' else seg
    kd = keys(parts['de'].split('\n    en:{')[0]); kl = keys(seg)
    print(L, 'missing:', sorted(kd - kl) or 'none', '| extra:', sorted(kl - kd) or 'none')
print('written', OUT, len(p) // 1024, 'kB')
