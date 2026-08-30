# -*- coding: utf-8 -*-
"""Traegt den inneren Wert in die Seite ein - auf jede Firmenseite.

Der Eingriff ist bewusst klein und wiederholbar: ein eigener JSON-Block neben
den vorhandenen, eine Kennzahlkachel, ein Rechenweg hinter dem Klick, dazu die
Texte in drei Sprachen. Alles ueber Marker, damit derselbe Aufruf morgen
dieselbe Stelle findet und nichts doppelt einfuegt.

    python werkzeuge/seite.py            # eintragen und pruefen
    python werkzeuge/seite.py --pruefen  # nur sagen, was passieren wuerde
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402
import wert as W                                                # noqa: E402

MARKE = "/* wertung: eingetragen */"

# Die Umstellung auf Dollar. Sie stand zuerst als Einmalskript daneben - ein
# Fehler: Die erzeugende Pipeline schreibt nvidia-oekosystem.html vollstaendig
# neu, jeder Upload haette sie stillschweigend entfernt. Deshalb gehoert sie
# hierher, zu allem anderen, was nach einem Upload wieder drueberlaufen muss.
USD_MARKE = "const IN_USD"
USD_ANKER = "const F = D.firmen, K = D.kurse;\nconst SCHLUESSEL = Object.keys(F);\n"
USD_BLOCK = """
/* ---------- Alles in Dollar ----------
   Zehn der 66 Firmen bilanzieren nicht in Dollar. Bis hierher stehen ihre
   Kurse und Quartalszahlen in der Heimatwaehrung, weil Kurs und Gewinn je
   Aktie dieselbe Einheit brauchen; sonst wird das KGV falsch. Ab hier wird
   beides mit demselben Faktor umgerechnet, und genau deshalb bleibt das KGV
   richtig.

   Ein fester Kurs vom Datenstand, kein historischer je Tag: Verhaeltniszahlen
   sind gegen einen konstanten Faktor immun, und die Kurskurven behalten ihre
   Form. Nicht umgerechnet wird, was keine Waehrung traegt - Aktienzahlen,
   Margen, Steuerquoten, Wachstumsraten. Wer die Heimatwaehrung sehen will,
   setzt IN_USD auf false. */
const IN_USD = true;
if(IN_USD) for(const k of SCHLUESSEL){
  const e = F[k], fx = e.fx_usd;
  if(e.waehrung === 'USD' || !fx || !isFinite(fx)) continue;
  const um = v => (typeof v === 'number' && isFinite(v)) ? v*fx : v;
  const tief = o => { for(const n in o){
    const v = o[n];
    if(typeof v === 'number') o[n] = isFinite(v) ? v*fx : v;
    else if(v && typeof v === 'object') tief(v);
  }};
  for(const f of ['kurs','eps_ttm','eps_q','umsatz_ttm','marktkap','marktkap_yf'])
    e[f] = um(e[f]);
  for(const q of (e.quartale||[]))
    for(const f of ['umsatz','brutto','operativ','netto','eps']) q[f] = um(q[f]);
  if(K[k] && K[k].close) K[k].close = K[k].close.map(um);
  if(typeof SEG !== 'undefined' && SEG[k]) tief(SEG[k]);
  if(typeof CF !== 'undefined' && CF[k]) tief(CF[k]);
  e.waehrung_heim = e.waehrung;
  e.waehrung = 'USD';
}
"""

# Der Firmenkopf soll die Bilanzwaehrung nennen, nicht die Anzeigewaehrung.
# Nach der Umrechnung steht in e.waehrung ueberall USD; die Herkunft haelt
# e.waehrung_heim fest. Ohne diesen Griff meldet die Zeile bei SK hynix
# "Bilanz in USD, Anzeige in USD" - beides richtig geschrieben und trotzdem
# falsch. Zwei Fassungen des Ankers, weil die erzeugende Pipeline die Zeile
# zwischendurch geaendert hat.
KOPF_VARIANTEN = [
    "       &middot; ${T('bilanz_in')} ${w}, ${T('anzeige_usd')}${e.cik?` &middot; SEC-CIK ${e.cik}`:''}</p>",
    "       &middot; ${T('bilanz_in')} ${w}${e.cik?` &middot; SEC-CIK ${e.cik}`:''}</p>",
]
KOPF_NEU = ("       &middot; ${T('bilanz_in')} ${e.waehrung_heim || w}"
            "${e.waehrung_heim?`, ${T('anzeige_usd')}`:''}"
            "${e.cik?` &middot; SEC-CIK ${e.cik}`:''}</p>")

TEXTE = {
    "kz_wert": {
        "de": "Innerer Wert",
        "en": "Intrinsic value",
        "mn": "\u0411\u043e\u0434\u0438\u0442 \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "kz_wert_verh": {
        "de": "Kurs \u00f7 Wert",
        "en": "price \u00f7 value",
        "mn": "\u0425\u0430\u043d\u0448 \u00f7 \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "wert_frage": {
        "de": "Was ist die Firma wert, wenn man den Kurs nicht kennt?",
        "en": "What is the company worth if you do not look at the share price?",
        "mn": "\u0425\u0430\u043d\u0448\u044b\u0433 \u0445\u0430\u0440\u0430\u0445\u0433\u04af\u0439\u0433\u044d\u044d\u0440 "
              "\u043a\u043e\u043c\u043f\u0430\u043d\u0438 \u044f\u043c\u0430\u0440 \u04af\u043d\u044d\u0442\u044d\u0439 \u0432\u044d?",
    },
    "wert_s1": {
        "de": "Freier Cashflow als Ausgangspunkt: operativer Cashflow minus Investitionen, "
              "aus den Jahresabschluessen",
        "en": "Free cash flow as the starting point: operating cash flow minus capital "
              "expenditure, from the annual filings",
        "mn": "\u0427\u04e9\u043b\u04e9\u04e9\u0442 \u043c\u04e9\u043d\u0433\u04e9\u043d \u0443\u0440\u0441\u0433\u0430\u043b: "
              "\u04af\u0439\u043b \u0430\u0436\u0438\u043b\u043b\u0430\u0433\u0430\u0430\u043d\u044b \u0443\u0440\u0441\u0433\u0430\u043b "
              "\u0445\u0430\u0441\u0430\u0445 \u043a\u0430\u043f\u0438\u0442\u0430\u043b \u0437\u0430\u0440\u0434\u0430\u043b",
    },
    "wert_s2": {
        "de": "Zehn Jahre fortgeschrieben, das Anfangswachstum klingt auf drei Prozent ab",
        "en": "Projected ten years, the initial growth fading to three per cent",
        "mn": "\u0410\u0440\u0432\u0430\u043d \u0436\u0438\u043b\u044d\u044d\u0440 \u0442\u04e9\u0441\u04e9\u04e9\u043b\u0436, "
              "\u04e9\u0441\u04e9\u043b\u0442 \u0433\u0443\u0440\u0432\u0430\u043d \u0445\u0443\u0432\u044c \u0440\u0443\u0443 \u0431\u0443\u0443\u0440\u043d\u0430",
    },
    "wert_s3": {
        "de": "Abgezinst mit zehn Prozent, dazu der Endwert fuer die Zeit danach",
        "en": "Discounted at ten per cent, plus the terminal value for everything after",
        "mn": "\u0410\u0440\u0432\u0430\u043d \u0445\u0443\u0432\u0438\u0430\u0440 \u0445\u04af\u04af\u0433\u044d\u044d\u0440 "
              "\u0445\u04e9\u0440\u0432\u04af\u04af\u043b\u0436, \u0434\u044d\u044d\u0440 \u043d\u044c \u044d\u0446\u0441\u0438\u0439\u043d \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "wert_s4": {
        "de": "Nettoschulden abgezogen, durch die Aktienzahl geteilt",
        "en": "Net debt deducted, divided by the share count",
        "mn": "\u0426\u044d\u0432\u044d\u0440 \u04e9\u0440\u0438\u0439\u0433 \u0445\u0430\u0441\u0430\u0436, "
              "\u0445\u0443\u0432\u044c\u0446\u0430\u0430\u043d\u044b \u0442\u043e\u043e\u043d\u0434 \u0445\u0443\u0432\u0430\u0430\u043d\u0430",
    },
    "wert_bedeutet": {
        "de": "Der Markt zahlt das {x}-fache dessen, was diese Rechnung ergibt. Ueber "
              "eins heisst: teurer als die Rechnung, unter eins: billiger. {y} Prozent "
              "des Ergebnisses stecken im Endwert, also in der Annahme ueber Jahr elf "
              "und danach.",
        "en": "The market pays {x} times what this calculation produces. Above one means "
              "dearer than the calculation, below one cheaper. {y} per cent of the result "
              "sits in the terminal value, that is in the assumption about year eleven "
              "and beyond.",
        "mn": "\u0417\u0430\u0445 \u0437\u044d\u044d\u043b \u044d\u043d\u044d \u0442\u043e\u043e\u0446\u043e\u043e\u043d\u043e\u043e\u0441 "
              "{x} \u0434\u0430\u0445\u0438\u043d \u0438\u0445 \u0442\u04e9\u043b\u0436 \u0431\u0430\u0439\u043d\u0430. "
              "\u04ae\u0440 \u0434\u04af\u043d\u0433\u0438\u0439\u043d {y} \u0445\u0443\u0432\u044c \u043d\u044c "
              "\u044d\u0446\u0441\u0438\u0439\u043d \u04af\u043d\u044d \u0446\u044d\u043d\u044d\u0434 \u0431\u0430\u0439\u043d\u0430.",
    },
    "wert_nicht": {
        "de": "Keine Prognose und kein Kursziel. Der Abzinssatz ist gesetzt, nicht "
              "gemessen: Ein Lehrbuch-WACC zoege sein Beta aus der Kursreihe, dann haenge "
              "der angeblich kursunabhaengige Wert wieder am Kurs. Wer die Huerde auf acht "
              "oder zwoelf Prozent stellt, bekommt eine deutlich andere Zahl.",
        "en": "Not a forecast and not a price target. The discount rate is set, not "
              "measured: a textbook WACC would take its beta from the price series, and "
              "then the supposedly price-independent value would hang on the price again. "
              "Set the hurdle at eight or twelve per cent and the number changes markedly.",
        "mn": "\u0422\u0430\u0430\u043c\u0430\u0433\u043b\u0430\u043b \u0431\u0438\u0448, "
              "\u0437\u043e\u0440\u0438\u043b\u0442\u043e\u0442 \u0445\u0430\u043d\u0448 \u0431\u0438\u0448. "
              "\u0425\u04af\u04af\u0433\u0438\u0439\u043d \u0442\u04af\u0432\u0448\u0438\u043d \u043d\u044c "
              "\u0445\u044d\u043c\u0436\u0438\u0433\u0434\u0441\u044d\u043d \u0431\u0438\u0448, \u0442\u043e\u0433\u0442\u043e\u043e\u0441\u043e\u043d.",
    },
    "wert_guthaben": {
        "de": "Nettoguthaben: mehr Geld als Schulden, deshalb addiert",
        "en": "Net cash: more money than debt, therefore added",
        "mn": "Цэвэр бэлэн мөнгө: өрөөс их тул нэмнэ",
    },
    "wert_schulden": {
        "de": "Nettoschulden: mehr Schulden als Geld, deshalb abgezogen",
        "en": "Net debt: more debt than money, therefore deducted",
        "mn": "Цэвэр өр: бэлэн мөнгөнөөс их тул хасна",
    },
    "kz_rendite_q": {
        "de": "Gewinnrendite, letztes Quartal",
        "en": "Earnings yield, latest quarter",
        "mn": "Ашгийн өгөөж, сүүлийн улирал",
    },
    "kz_rendite_ttm": {
        "de": "Gewinnrendite, vier Quartale",
        "en": "Earnings yield, four quarters",
        "mn": "Ашгийн өгөөж, дөрвөн улирал",
    },
    "kz_rendite_q_sub": {
        "de": "letztes Quartal mal vier, geteilt durch den Kurs",
        "en": "latest quarter times four, divided by the price",
        "mn": "сүүлийн улирлыг дөрөв дахин, ханшид хуваасан",
    },
    "kz_rendite_ttm_sub": {
        "de": "vier Quartale geteilt durch den Kurs",
        "en": "four quarters divided by the price",
        "mn": "дөрвөн улирлыг ханшид хуваасан",
    },
    "kz_rendite_verlust": {
        "de": "Verlust, keine Rendite",
        "en": "loss, no yield",
        "mn": "алдагдалтай тул өгөөжгүй",
    },
    "wert_leer": {
        "de": "nicht berechenbar",
        "en": "not calculable",
        "mn": "\u0442\u043e\u043e\u0446\u043e\u043e\u043b\u043e\u0445 \u0431\u043e\u043b\u043e\u043c\u0436\u0433\u04af\u0439",
    },
}

# --- 0. Rechenhilfe fuer die Gewinnrendite ---------------------------------
# Der Kehrwert des KGV, aber als Rendite gelesen: Wieviel Prozent des
# eingesetzten Kurses verdient die Firma im Jahr? Das laesst sich unmittelbar
# gegen eine Anleiherendite halten und gegen die zehn Prozent, mit denen der
# innere Wert abgezinst wird. Ein Verlust ergibt eine negative Rendite - die
# wird gezeigt, nicht versteckt, denn sie ist eine richtige Aussage.
HILFEN = """
const rendite = (eps, kurs)=> (eps==null || !kurs) ? null : eps/kurs*100;
"""

# --- 1. Kennzahlkachel ------------------------------------------------------
UMSATZ_ALT = "    [T('kz_umsatz_yoy'), pf(e.umsatz_yoy), T('kz_letztes_q'), null],\n"
UMSATZ_NEU = (UMSATZ_ALT +
              "    /* gewinnrendite */\n"
              "    [T('kz_rendite_q'),\n"
              "     rendite(e.eps_q!=null ? e.eps_q*4 : null, e.kurs)!=null\n"
              "       ? pf(rendite(e.eps_q*4, e.kurs),1) : '\\u2013',\n"
              "     e.eps_q!=null ? T('kz_rendite_q_sub') : T('kz_rendite_verlust'), null],\n"
              "    [T('kz_rendite_ttm'),\n"
              "     rendite(e.eps_ttm, e.kurs)!=null ? pf(rendite(e.eps_ttm, e.kurs),1) : '\\u2013',\n"
              "     e.eps_ttm!=null ? T('kz_rendite_ttm_sub') : T('kz_rendite_verlust'), null],\n")

KACHEL_ALT = "    [T('kz_kurs'), kursF(e.kurs,w), e.kursdatum, null],\n"
KACHEL_NEU = ("    [T('kz_kurs'), kursF(e.kurs,w), e.kursdatum, null],\n"
              "    " + MARKE + "\n"
              "    [T('kz_wert'),\n"
              "     WERT[k] && WERT[k].wert!=null ? kursF(WERT[k].wert, WERT[k].waehrung||w) : '\\u2013',\n"
              "     WERT[k] && WERT[k].wert!=null\n"
              "       ? T('kz_wert_verh')+' '+nf(e.kurs/WERT[k].wert,2)\n"
              "       : (WERT[k] ? (WERT[k].grund||'').split(' - ')[0] : T('wert_leer')),\n"
              "     WERT[k] && WERT[k].wert!=null ? 'wert' : null],\n")

# --- 2. Rechenweg hinter dem Klick -----------------------------------------
ERKL = """  else if(art==='wert'){
    const v=WERT[k];
    if(!v || v.wert==null) return null;
    const wv=v.waehrung||w;
    titel=T('kz_wert'); frage=T('wert_frage');
    schritte=[
      {text:T('wert_s1'), rechnung:`${gross(v.fcf_basis,wv)}`,
       zusatz:Object.keys(v.fcf||{}).sort().map(j=>j+': '+gross(v.fcf[j],wv)).join('   ')},
      {text:T('wert_s2'), rechnung:`${pf(100*v.wachstum,1)}  \\u2192  ${pf(3,0)}`},
      {text:T('wert_s3'), rechnung:`${gross(v.unternehmenswert,wv)}`},
      {text:T('wert_s4'),
       // Klammern, weil ohne sie Punkt vor Strich gilt und die Zeile etwas
       // anderes behauptet als die Rechnung. Und bei Nettoguthaben wird
       // addiert statt zweimal minus zu schreiben.
       rechnung:`(${gross(v.unternehmenswert,wv)}  ${v.nettoschulden<0?'+':'\\u2212'}  ${gross(Math.abs(v.nettoschulden),wv)})  \\u00f7  ${nf(v.aktien/1e6,0)} Mio  =  ${kursF(v.wert,wv)}`,
       zusatz:v.nettoschulden<0?T('wert_guthaben'):T('wert_schulden')}];
    ergebnis=kursF(v.wert,wv);
    bedeutet=T('wert_bedeutet').split('{x}').join(nf(e.kurs/v.wert,2))
             .split('{y}').join(nf(100*v.endwertanteil,0));
    nicht=T('wert_nicht');
  }
"""


def eintragen(pruefen=False):
    pfad = os.path.join(b.WURZEL, "nvidia-oekosystem.html")
    s = open(pfad, encoding="utf-8").read()
    daten = json.load(open(b._pfad("wert.json"), encoding="utf-8"))
    mit = sum(1 for v in daten.values() if v.get("wert") is not None)
    schritte = []

    # Datenblock: ersetzen wenn da, sonst hinter den letzten JSON-Block setzen.
    block = '<script id="wertung" type="application/json">%s</script>' % json.dumps(
        daten, ensure_ascii=False, separators=(",", ":"))
    if 'id="wertung"' in s:
        s = re.sub(r'<script id="wertung" type="application/json">.*?</script>',
                   lambda _: block, s, count=1, flags=re.S)
        schritte.append("Datenblock ersetzt")
    else:
        anker = re.search(r'(<script id="operativ" type="application/json">.*?</script>\n)', s, re.S)
        s = s[:anker.end()] + block + "\n" + s[anker.end():]
        schritte.append("Datenblock eingefuegt")

    if "const WERT" not in s:
        s = s.replace("const OP = JSON.parse(document.getElementById('operativ').textContent);",
                      "const OP = JSON.parse(document.getElementById('operativ').textContent);\n"
                      "const WERT = JSON.parse(document.getElementById('wertung').textContent);", 1)
        schritte.append("WERT verdrahtet")

    # Dollar-Umstellung: muss vor allem anderen stehen, weil die Kacheln und die
    # Wertrechnung die umgerechneten Felder lesen.
    if USD_MARKE not in s:
        if USD_ANKER not in s:
            sys.exit("Ankerstelle fuer die Dollar-Umstellung nicht gefunden.")
        s = s.replace(USD_ANKER, USD_ANKER + USD_BLOCK, 1)
        schritte.append("Dollar-Umstellung eingefuegt")
    if "e.waehrung_heim || w" not in s:
        for variante in KOPF_VARIANTEN:
            if variante in s:
                s = s.replace(variante, KOPF_NEU, 1)
                schritte.append("Firmenkopf nennt die Bilanzwaehrung")
                break
        else:
            print("   ! Firmenkopf nicht gefunden - die Zeile hat sich geaendert, "
                  "sie meldet jetzt womoeglich USD als Bilanzwaehrung")

    if "const rendite" not in s:
        s = s.replace("const WERT = JSON.parse(document.getElementById('wertung').textContent);",
                      "const WERT = JSON.parse(document.getElementById('wertung').textContent);"
                      + HILFEN, 1)
        schritte.append("Renditehilfe eingefuegt")

    if MARKE not in s:
        if KACHEL_ALT not in s:
            sys.exit("Kennzahlliste nicht gefunden - die Seite hat sich geaendert.")
        s = s.replace(KACHEL_ALT, KACHEL_NEU, 1)
        schritte.append("Wertkachel eingefuegt")

    if "/* gewinnrendite */" not in s:
        if UMSATZ_ALT not in s:
            sys.exit("Umsatzzeile nicht gefunden - die Seite hat sich geaendert.")
        s = s.replace(UMSATZ_ALT, UMSATZ_NEU, 1)
        schritte.append("Renditekacheln eingefuegt")

    # Der Rechenweg wird bei jedem Lauf ersetzt, nicht nur beim ersten - sonst
    # kommt eine Korrektur an der Darstellung nie auf der Seite an. Deshalb
    # steht er zwischen zwei Marken.
    block_auf, block_zu = "  /* wert-rechenweg */\n", "  /* ende wert-rechenweg */\n"
    neu = block_auf + ERKL + block_zu
    if block_auf in s:
        s = re.sub(re.escape(block_auf) + ".*?" + re.escape(block_zu),
                   lambda _: neu, s, count=1, flags=re.S)
        schritte.append("Rechenweg ersetzt")
    else:
        # In die *aktive* Erklaerung, also die letzte im Text definierte.
        stelle = s.rfind("  else return null;")
        if stelle < 0:
            sys.exit("Erklaerungskette nicht gefunden.")
        s = s[:stelle] + neu + s[stelle:]
        schritte.append("Rechenweg eingefuegt")

    # Texte: immer neu schreiben, damit Formulierungsaenderungen ankommen.
    m = re.search(r'(<script[^>]*id="texte"[^>]*>)(.*?)(</script>)', s, re.S)
    TX = json.loads(m.group(2))
    TX["t"].update(TEXTE)
    s = s[:m.start(2)] + json.dumps(TX, ensure_ascii=False, separators=(",", ":")) + s[m.end(2):]
    schritte.append("Texte aktualisiert (%d Schluessel)" % len(TEXTE))

    print("Innerer Wert fuer %d von %d Firmen, %d ohne Zahl."
          % (mit, len(daten), len(daten) - mit))
    for x in schritte:
        print("   " + x)
    if pruefen:
        print("\n--pruefen: nichts geschrieben.")
        return
    open(pfad, "w", encoding="utf-8", newline="").write(s)
    print("\n-> %s" % pfad)


if __name__ == "__main__":
    eintragen("--pruefen" in sys.argv)
