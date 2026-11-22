# -*- coding: utf-8 -*-
# Aktionaersstruktur auf der Firmenseite: gestapelte Balken alle zwei Monate
# (wem die Aktien gehoeren), darunter die Nettokaeufe je Anlegergruppe und die
# Zahl der Kleinaktionaere. Die Daten liegen in aktionaere.json im Repository,
# gebaut von speicher_analysen/rechnungen/10_aktionaere_seite.py.
#
# Gleiches Muster wie die Fabrikliste in seite.py: Datenblock, Hilfsfunktion
# und Stil zwischen Marken, bei jedem Lauf ersetzt, damit der Tageslauf den
# Block nach jedem Upload der Pipeline wieder auftraegt. seite.eintragen ruft
# eintragen_in am Ende auf. Nur Definitionen, beim Import passiert nichts.

import json
import os
import re

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HILFE = r"""
const aktKurslinie = (tage, kurs)=>{
  // Gleiche Geometrie wie gestapelt(), eigene Skala fuer den Kurs.
  const breite=chartBreite(), hoehe=schmal()?250:300;
  const ml=schmal()?42:58, mr=8, mo=14, mu=24;
  const iw=breite-ml-mr, ih=hoehe-mo-mu;
  const hoch=Math.max(...kurs), hi=hoch*1.12;
  const X=i=>ml+iw*(i+0.5)/tage.length, Y=v=>mo+ih-v/hi*ih;
  const pkt=kurs.map((v,i)=>`${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
  const imax=kurs.indexOf(hoch), n=kurs.length-1;
  const marke=(i,anker)=>`<circle cx="${X(i).toFixed(1)}" cy="${Y(kurs[i]).toFixed(1)}" r="3.2" fill="var(--tinte)"/>
    <text x="${X(i).toFixed(1)}" y="${(Y(kurs[i])-8).toFixed(1)}" text-anchor="${anker}" font-family="var(--mono)"
      font-size="10.5" fill="var(--tinte)" stroke="var(--flaeche)" stroke-width="3" paint-order="stroke">${nf(kurs[i],0)} $</text>`;
  return `<polyline points="${pkt}" fill="none" stroke="var(--flaeche)" stroke-width="5" stroke-linejoin="round"/>
    <polyline points="${pkt}" fill="none" stroke="var(--tinte)" stroke-width="2" stroke-linejoin="round"/>
    ${marke(0,'start')}${imax!==0&&imax!==n?marke(imax,'middle'):''}${marke(n,'end')}`;
};
const aktionaerBlock = (k)=>{
  const a = AKTIONAERE[k];
  if(!a || !a.stichtage) return '';
  const tx = (o)=> (o && (o[L]||o.de)) || '';
  const tage = a.stichtage, fenster = tage.slice(1);
  const reihe = (g, liste)=>({name:tx(g.name), werte:Object.fromEntries(liste.map((t,i)=>[t, g.werte[i]]))});
  let bestand = gestapelt(tage, a.gruppen.map(g=>reihe(g,tage)),
    {labelY:v=>nf(v,0), farben:a.gruppen.map(g=>g.farbe)});
  bestand = bestand.replace('</svg>', aktKurslinie(tage, a.kurs_usd)+'</svg>');
  const handel = gestapelt(fenster, a.netto.map(g=>reihe(g,fenster)),
    {labelY:v=>nf(Math.abs(v)<1e-6?0:v,0), farben:a.netto.map(g=>g.farbe), hoehe:schmal()?200:230});
  const legende = (gs)=> gs.map(g=>`<span><i style="background:${g.farbe}"></i>${tx(g.name)}</span>`).join('');
  const klein = a.kleinaktionaere.map(z=>`<tr><td>${z.stichtag}</td><td>${nf(z.anzahl,0)}</td>
    <td>${nf(z.aktien_mio,1)}</td></tr>`).join('');
  return `<section class="abschnitt aktionaere">
    <h3 class="an-titel">${T('akt_titel')}</h3>
    <p class="akt-kopf">${tx(a.kopf)}</p>
    <p class="akt-these">${tx(a.these)}</p>
    <h4 class="akt-h">${T('akt_bestand')}</h4>
    <div class="akt-legende">${legende(a.gruppen)}<span><i class="akt-linie"></i>${T('akt_kurs')}</span></div>
    <div class="chart">${bestand}</div>
    <h4 class="akt-h">${T('akt_handel')}</h4>
    <div class="akt-legende">${legende(a.netto)}</div>
    <div class="chart">${handel}</div>
    <h4 class="akt-h">${T('akt_klein')}</h4>
    <table class="akt-tab"><thead><tr><th>${T('akt_stichtag')}</th><th>${T('akt_anzahl')}</th>
      <th>${T('akt_aktien')}</th></tr></thead><tbody>${klein}</tbody></table>
    <p class="akt-fuss">${tx(a.hinweis)} &middot; ${T('akt_stand')} ${AKTIONAERE._stand}</p>
  </section>`;
};
"""

CSS = """
.aktionaere .akt-kopf{font-family:var(--mono);font-size:12.5px;color:var(--tinte);margin:0 0 6px}
.aktionaere .akt-these{font-size:14.5px;line-height:1.55;color:var(--gedaempft);margin:0 0 14px;max-width:74ch}
.akt-h{font-family:var(--mono);font-size:10.5px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;
  color:var(--schwach);margin:18px 0 6px}
.akt-legende{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12.5px;color:var(--gedaempft);margin:0 0 6px}
.akt-legende i{display:inline-block;width:10px;height:10px;margin-right:5px;vertical-align:-1px}
.akt-legende i.akt-linie{width:16px;height:2px;background:var(--tinte);vertical-align:3px}
.aktionaere .chart{max-width:680px}
.aktionaere .akt-tab{width:auto;min-width:0;border-collapse:collapse;font-size:13px;margin:0 0 10px}
.akt-tab th, .akt-tab td{padding:4px 14px 4px 0;text-align:right;font-family:var(--mono)}
.akt-tab th:first-child, .akt-tab td:first-child{text-align:left}
.akt-tab th{font-size:10.5px;font-weight:500;color:var(--schwach);border-bottom:1px solid var(--linie-stark)}
.akt-fuss{font-family:var(--mono);font-size:11.5px;line-height:1.5;color:var(--schwach);max-width:90ch;margin:4px 0 0}
"""

TEXTE = {
    "akt_titel": {"de": "Wem die Aktien gehören", "en": "Who owns the shares"},
    "akt_bestand": {"de": "Bestand je Gruppe, Mio Aktien, alle zwei Monate", "en": "Holdings by group, m shares, every two months"},
    "akt_kurs": {"de": "Kurs am Stichtag in USD (eigene Skala)", "en": "Price on the date in USD (own scale)"},
    "akt_handel": {"de": "Nettokäufe an der Börse je zwei Monate, Mio Aktien", "en": "Net exchange purchases per two months, m shares"},
    "akt_klein": {"de": "Kleinaktionäre laut Aktienbuch (unter 1 %)", "en": "Small shareholders per register (below 1 %)"},
    "akt_stichtag": {"de": "Stichtag", "en": "Date"},
    "akt_anzahl": {"de": "Aktionäre", "en": "Holders"},
    "akt_aktien": {"de": "Aktien, Mio", "en": "Shares, m"},
    "akt_stand": {"de": "Stand", "en": "As of"},
}

def _zwischen(s, auf, zu, neu, anker_vor):
    block = auf + neu.strip() + "\n" + zu
    if auf in s:
        return re.sub(re.escape(auf) + ".*?" + re.escape(zu), lambda _: block, s, count=1, flags=re.S), "ersetzt"
    return s.replace(anker_vor, block + anker_vor, 1), "eingefuegt"

def eintragen_in(s):
    pfad = os.path.join(WURZEL, "aktionaere.json")
    if not os.path.exists(pfad) or "${fabrikBlock(k)}" not in s:
        return s, ["Aktionaere: keine Daten oder kein Anker, uebersprungen"]
    schritte = []
    daten = json.load(open(pfad, encoding="utf-8"))
    block = ('<script id="aktionaere" type="application/json">%s</script>'
             % json.dumps(daten, ensure_ascii=False, separators=(",", ":")))
    if 'id="aktionaere"' in s:
        s = re.sub(r'<script id="aktionaere" type="application/json">.*?</script>', lambda _: block, s, count=1, flags=re.S)
        schritte.append("Aktionaersblock ersetzt")
    else:
        m = re.search(r'(<script id="wertung" type="application/json">.*?</script>\n?)', s, re.S)
        s = s[:m.end()] + block + "\n" + s[m.end():]
        schritte.append("Aktionaersblock eingefuegt")
    if "const AKTIONAERE" not in s:
        s = s.replace("const WERT = JSON.parse(document.getElementById('wertung').textContent);",
                      "const WERT = JSON.parse(document.getElementById('wertung').textContent);\n"
                      "const AKTIONAERE = JSON.parse(document.getElementById('aktionaere').textContent);", 1)
    s, wie = _zwischen(s, "/* aktionaer-hilfe */\n", "/* ende aktionaer-hilfe */\n", HILFE, "const rendite = ")
    schritte.append("Aktionaershilfe " + wie)
    if "${aktionaerBlock(k)}" not in s:
        s = s.replace("${fabrikBlock(k)}", "${fabrikBlock(k)}${aktionaerBlock(k)}", 1)
        schritte.append("Aktionaere auf der Firmenseite verdrahtet")
    s, wie = _zwischen(s, "/* aktionaere: anfang */\n", "/* aktionaere: ende */\n", CSS,
                       "/* fabriken: anfang */\n" if "/* fabriken: anfang */\n" in s else ".kz{background:var(--flaeche)")
    schritte.append("Aktionaers-CSS " + wie)
    m = re.search(r'(<script[^>]*id="texte"[^>]*>)(.*?)(</script>)', s, re.S)
    TX = json.loads(m.group(2))
    TX["t"].update(TEXTE)
    s = s[:m.start(2)] + json.dumps(TX, ensure_ascii=False, separators=(",", ":")) + s[m.end(2):]
    schritte.append("Aktionaers-Texte aktualisiert")
    return s, schritte
