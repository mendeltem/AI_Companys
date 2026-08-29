# -*- coding: utf-8 -*-
"""Quartalsberichte der Firmen aus nvidia-oekosystem.html einsammeln, laden und
in Text verwandeln, aus dem sich Embeddings rechnen lassen.

Vier Schritte, jeder einzeln aufrufbar und jeder wiederholbar, ohne dass
schon Erledigtes noch einmal laeuft:

    python werkzeuge/berichte.py sammeln   # Arbeitsliste bauen (Netz: SEC-Verzeichnisse)
    python werkzeuge/berichte.py laden     # Dokumente herunterladen
    python werkzeuge/berichte.py text      # Text herausziehen und stueckeln
    python werkzeuge/berichte.py status    # Ueberblick, was da ist und was fehlt

Zwei Quellen speisen die Arbeitsliste. Erstens die Links, die schon in der
Seite stehen: fuer 18 Firmen von Hand gesammelte Pressemitteilungen,
Praesentationen und Mitschnitte, teils bis 2013 zurueck. Zweitens EDGAR: fuer
jede Firma mit CIK werden die Einreichungen abgefragt und daraus die
Ergebnisdokumente gezogen. Beides zusammen, doppelte URLs fallen weg.

Die SEC verlangt im User-Agent eine Kontaktadresse und deckelt die Frequenz.
Beides steht unten in KONTAKT und TAKT. Ohne Adresse antwortet sec.gov mit 403.
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

# ---------------------------------------------------------------- Einstellung

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEITE = os.path.join(WURZEL, "nvidia-oekosystem.html")
ZIEL = os.environ.get("BERICHTE_ZIEL", os.path.join(os.path.dirname(WURZEL), "AI_companys_berichte"))

# Die SEC bittet um eine erreichbare Adresse statt eines anonymen Browser-Strings.
# Sie geht ausschliesslich an sec.gov und data.sec.gov.
KONTAKT = os.environ.get("SEC_KONTAKT", "mendeltem@googlemail.com")
UA_SEC = "AI_Companys Forschungsprojekt %s" % KONTAKT
UA_ALLGEMEIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI_Companys/1.0"

# Sekunden zwischen zwei Anfragen an denselben Host. Die SEC erlaubt zehn
# Anfragen je Sekunde; fuenf sind hoeflich und immer noch schnell genug.
TAKT = {"www.sec.gov": 0.2, "data.sec.gov": 0.2}
TAKT_SONST = 1.0

# Formulare, in denen Quartalszahlen stecken. 8-K traegt die Pressemitteilung
# als Anlage, 6-K ist das Gegenstueck fuer auslaendische Emittenten.
FORMULARE = {"10-Q", "10-K", "8-K", "6-K", "20-F", "40-F", "10-Q/A", "10-K/A", "8-K/A"}

# Anlagen, die Text tragen. Alles andere (XBRL, Bilder, Rechenblaetter) bleibt
# liegen; die Zahlen selbst kommen ohnehin schon aus den XBRL-Daten der Seite.
TEXTENDUNGEN = {".htm", ".html", ".txt", ".pdf"}
MEDIENENDUNGEN = {".mp3", ".mp4", ".m4a", ".wav"}

_letzter_zugriff = {}


def _pfad(*teile):
    return os.path.join(ZIEL, *teile)


def _sicher(name, grenze=120):
    """Dateinamen, die Windows akzeptiert."""
    name = unquote(name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:grenze] or "datei"


def hole(url, kopf=None, versuche=4):
    """Eine Anfrage, mit Takt je Host, Wiederholung und ausgepacktem gzip."""
    host = urlparse(url).netloc
    takt = TAKT.get(host, TAKT_SONST)
    warten = takt - (time.time() - _letzter_zugriff.get(host, 0))
    if warten > 0:
        time.sleep(warten)
    kopfzeilen = {
        "User-Agent": UA_SEC if host.endswith("sec.gov") else UA_ALLGEMEIN,
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
    }
    if kopf:
        kopfzeilen.update(kopf)
    letzter = None
    for versuch in range(versuche):
        try:
            anfrage = urllib.request.Request(url, headers=kopfzeilen)
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                roh = antwort.read()
                if antwort.headers.get("Content-Encoding") == "gzip":
                    roh = gzip.decompress(roh)
                _letzter_zugriff[host] = time.time()
                return roh, antwort.headers.get("Content-Type", ""), antwort.status
        except urllib.error.HTTPError as f:
            letzter = f
            _letzter_zugriff[host] = time.time()
            # 403 und 404 aendern sich beim zweiten Versuch nicht.
            if f.code in (403, 404, 410):
                break
            time.sleep(2 ** versuch)
        except Exception as f:
            letzter = f
            _letzter_zugriff[host] = time.time()
            time.sleep(2 ** versuch)
    raise letzter


def daten_der_seite():
    """Die drei JSON-Bloecke aus der HTML-Datei, die hier gebraucht werden."""
    s = open(SEITE, encoding="utf-8").read()

    def blob(kennung):
        treffer = re.search(r'<script[^>]*id="%s"[^>]*>(.*?)</script>' % kennung, s, re.S)
        return json.loads(treffer.group(1)) if treffer else {}

    return blob("daten"), blob("quellenlinks")


# ------------------------------------------------------------------- sammeln

def _cik_verzeichnis():
    """Ticker auf CIK, fuer die Firmen, bei denen in den Daten keiner steht."""
    roh, _, _ = hole("https://www.sec.gov/files/company_tickers.json")
    tabelle = json.loads(roh)
    return {e["ticker"].upper(): str(e["cik_str"]).zfill(10) for e in tabelle.values()}


def _einreichungen(cik, nur_neue=False):
    """Alle Einreichungen einer Firma, auch die aelteren Zusatzdateien.

    Mit nur_neue bleibt es beim Block 'recent'. Der reicht rund tausend
    Einreichungen weit zurueck und damit fuer den taeglichen Blick allemal;
    er spart je Firma mehrere Anfragen.
    """
    roh, _, _ = hole("https://data.sec.gov/submissions/CIK%s.json" % cik)
    d = json.loads(roh)
    zeilen = []

    def anhaengen(block):
        felder = ("accessionNumber", "filingDate", "reportDate", "form", "primaryDocument",
                  "primaryDocDescription")
        if not block or "accessionNumber" not in block:
            return
        for i in range(len(block["accessionNumber"])):
            zeilen.append({f: (block.get(f) or [None] * (i + 1))[i] for f in felder})

    anhaengen(d.get("filings", {}).get("recent", {}))
    for zusatz in d.get("filings", {}).get("files", []):
        roh2, _, _ = hole("https://data.sec.gov/submissions/" + zusatz["name"])
        anhaengen(json.loads(roh2))
    return d.get("name", ""), zeilen


def _filing_dokumente(cik, zugang, primaer, form=""):
    """Aus dem Verzeichnis einer Einreichung die Textdokumente ziehen.

    Bei 10-Q, 10-K, 20-F und 40-F ist der Bericht selbst das Hauptdokument;
    dazu kommen Anlagen EX-99, falls vorhanden. Bei 8-K und 6-K steht auf dem
    Hauptdokument nur der Deckel mit zwei Saetzen, die Zahlen liegen in der
    Anlage EX-99 - deshalb dort nur die Anlagen, und eine Einreichung ohne
    solche Anlage faellt ganz heraus. Liegen bleiben XBRL, die generierten
    R-Dateien der Betrachtungsansicht, Bilder und alles ohne Endung aus
    TEXTENDUNGEN.
    """
    nur_anlagen = form.replace("/A", "") in ("8-K", "6-K")
    nummer = zugang.replace("-", "")
    basis = "https://www.sec.gov/Archives/edgar/data/%s/%s" % (int(cik), nummer)
    # Die Deckblattseite der Einreichung nennt zu jeder Datei ihren Typ
    # (EX-99.1, GRAPHIC, 10-Q). Aus den Dateinamen allein laesst sich das nicht
    # ablesen: NVIDIA nennt seine Pressemitteilung q1fy27pr.htm, andere
    # ex99-1.htm. Deshalb diese Seite statt des Verzeichnisses.
    roh, _, _ = hole("%s/%s-index.htm" % (basis, zugang))
    seite = roh.decode("utf-8", "replace")
    raus = []
    for zeile in re.findall(r"<tr[^>]*>(.*?)</tr>", seite, re.S):
        link = re.search(r'href="([^"]+)"', zeile)
        felder = [re.sub(r"<[^>]+>", "", f).replace("&nbsp;", " ").strip()
                  for f in re.findall(r"<td[^>]*>(.*?)</td>", zeile, re.S)]
        if not link or len(felder) < 5:
            continue
        pfad_url = link.group(1)
        name = os.path.basename(pfad_url)
        typ = felder[3].upper()
        beschreibung = felder[1]
        endung = os.path.splitext(name.lower())[1]
        if endung not in TEXTENDUNGEN:
            continue
        if name.startswith(zugang):                      # vollstaendige Einreichung, alles doppelt
            continue
        if typ.startswith("EX-99"):
            art = "Anlage %s%s" % (typ, (" · " + beschreibung) if beschreibung and beschreibung != typ else "")
        elif not nur_anlagen and (typ == form.upper() or (primaer and name.lower() == primaer.lower())):
            art = "Bericht %s" % form
        else:
            continue                                     # Zertifikate, XBRL, Bilder, Deckblatt
        raus.append({
            "url": "https://www.sec.gov" + pfad_url if pfad_url.startswith("/") else pfad_url,
            "name": name,
            "art": art,
            "bytes_erwartet": int(felder[4]) if felder[4].isdigit() else 0,
        })
    return raus


def sammeln(args):
    os.makedirs(ZIEL, exist_ok=True)
    D, Q = daten_der_seite()
    F = D["firmen"]
    arbeit = {}          # url -> Eintrag
    ab = args.ab

    # 1. Was schon in der Seite steht.
    for sym, quartale in Q.items():
        for ende, e in quartale.items():
            for d in e.get("dokumente", []):
                url = d["url"]
                arbeit[url] = {
                    "ticker": sym,
                    "firma": F.get(sym, {}).get("name", sym),
                    "quartal_ende": ende,
                    "eingereicht": e.get("eingereicht"),
                    "form": "kuratiert",
                    "art": d.get("name", ""),
                    "url": url,
                    "herkunft": "seite",
                }

    print("kuratierte Dokumente: %d aus %d Firmen" % (len(arbeit), len(Q)))

    if args.nur_kuratiert:
        _arbeitsliste_schreiben(arbeit)
        return

    # 2. EDGAR fuer alles, was eine CIK hat oder ueber den Ticker eine bekommt.
    verzeichnis = None
    ohne_cik = []
    for sym, e in F.items():
        cik = e.get("cik")
        if not cik:
            if verzeichnis is None:
                print("Ticker-Verzeichnis der SEC laden ...")
                verzeichnis = _cik_verzeichnis()
            cik = verzeichnis.get(sym.upper()) or verzeichnis.get(str(e.get("symbol", "")).upper())
            if not cik:
                ohne_cik.append(sym)
                continue
        cik = str(cik).zfill(10)
        try:
            name, zeilen = _einreichungen(cik)
        except Exception as f:
            print("  %-10s Einreichungen nicht abrufbar: %s" % (sym, f))
            ohne_cik.append(sym)
            continue
        passend = [z for z in zeilen
                   if z.get("form") in FORMULARE and (z.get("filingDate") or "") >= ab]
        passend.sort(key=lambda z: z.get("filingDate") or "", reverse=True)
        if args.grenze:
            passend = passend[: args.grenze]
        neu = 0
        for z in passend:
            try:
                for d in _filing_dokumente(cik, z["accessionNumber"], z.get("primaryDocument"), z.get("form", "")):
                    if d["url"] in arbeit:
                        continue
                    arbeit[d["url"]] = {
                        "ticker": sym,
                        "firma": e.get("name", name or sym),
                        "quartal_ende": z.get("reportDate"),
                        "eingereicht": z.get("filingDate"),
                        "form": z.get("form"),
                        "art": d["art"] + (" · " + (z.get("primaryDocDescription") or "")).rstrip(" ·"),
                        "url": d["url"],
                        "herkunft": "edgar",
                        "bytes_erwartet": d.get("bytes_erwartet", 0),
                        "zugang": z["accessionNumber"],
                    }
                    neu += 1
            except Exception as f:
                print("  %-10s %s: %s" % (sym, z.get("accessionNumber"), f))
        print("  %-10s CIK %s · %3d Einreichungen ab %s · %4d Dokumente" %
              (sym, cik, len(passend), ab, neu))

    if ohne_cik:
        print("\nohne SEC-Einreichungen (Heimatboerse, kein EDGAR): %s" % ", ".join(sorted(ohne_cik)))
    _arbeitsliste_schreiben(arbeit)


def _arbeitsliste_schreiben(arbeit):
    pfad = _pfad("arbeitsliste.jsonl")
    os.makedirs(ZIEL, exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as f:
        for e in sorted(arbeit.values(), key=lambda x: (x["ticker"], x.get("eingereicht") or "", x["url"])):
            e["pfad"] = os.path.join(
                e["ticker"],
                (e.get("quartal_ende") or e.get("eingereicht") or "ohne-datum"),
                _sicher(os.path.basename(urlparse(e["url"]).path) or "dokument"),
            )
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    firmen = len({e["ticker"] for e in arbeit.values()})
    print("\nArbeitsliste: %d Dokumente aus %d Firmen -> %s" % (len(arbeit), firmen, pfad))


# --------------------------------------------------------------------- laden

def _arbeitsliste_lesen():
    pfad = _pfad("arbeitsliste.jsonl")
    if not os.path.exists(pfad):
        sys.exit("Keine Arbeitsliste. Erst 'sammeln' laufen lassen.")
    return [json.loads(z) for z in open(pfad, encoding="utf-8") if z.strip()]


def laden(args):
    liste = _arbeitsliste_lesen()
    if not args.mit_audio:
        vorher = len(liste)
        liste = [e for e in liste
                 if os.path.splitext(urlparse(e["url"]).path)[1].lower() not in MEDIENENDUNGEN]
        if vorher != len(liste):
            print("%d Mediendateien uebersprungen (--mit-audio holt sie)" % (vorher - len(liste)))
    if args.firma:
        gewuenscht = {t.strip().upper() for t in args.firma.split(",")}
        liste = [e for e in liste if e["ticker"].upper() in gewuenscht]

    protokoll = _pfad("geladen.jsonl")
    fertig = {}
    if os.path.exists(protokoll):
        for z in open(protokoll, encoding="utf-8"):
            try:
                e = json.loads(z)
                fertig[e["url"]] = e
            except Exception:
                pass

    offen = [e for e in liste if fertig.get(e["url"], {}).get("status") != "ok"
             or not os.path.exists(_pfad("dateien", fertig[e["url"]]["pfad"]))]
    print("%d Dokumente in der Liste, %d bereits geladen, %d offen"
          % (len(liste), len(liste) - len(offen), len(offen)))

    gut = schlecht = 0
    bytes_gesamt = 0
    with open(protokoll, "a", encoding="utf-8") as mit:
        for i, e in enumerate(offen, 1):
            ziel = _pfad("dateien", e["pfad"])
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            try:
                roh, typ, status = hole(e["url"])
                teil = ziel + ".part"
                with open(teil, "wb") as f:
                    f.write(roh)
                os.replace(teil, ziel)
                eintrag = dict(e)
                eintrag.update({
                    "status": "ok", "bytes": len(roh), "content_type": typ,
                    "sha256": hashlib.sha256(roh).hexdigest(),
                    "geladen_am": date.today().isoformat(),
                })
                gut += 1
                bytes_gesamt += len(roh)
            except Exception as f:
                eintrag = dict(e)
                eintrag.update({"status": "fehler", "fehler": str(f)[:200]})
                schlecht += 1
            mit.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
            mit.flush()
            if i % 25 == 0 or i == len(offen):
                print("   %5d/%d  ok %d  Fehler %d  %.1f MB"
                      % (i, len(offen), gut, schlecht, bytes_gesamt / 1e6))
    print("fertig: %d geladen, %d Fehler, %.1f MB" % (gut, schlecht, bytes_gesamt / 1e6))


# ---------------------------------------------------------------------- text

class _NurText(HTMLParser):
    """Genug HTML-Entfernung fuer Pressemitteilungen und EDGAR-Dokumente."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stuecke = []
        self.stumm = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.stumm += 1
        elif tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table"):
            self.stuecke.append("\n")
        elif tag in ("td", "th"):
            self.stuecke.append("\t")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.stumm:
            self.stumm -= 1

    def handle_data(self, d):
        if not self.stumm:
            self.stuecke.append(d)

    def text(self):
        t = "".join(self.stuecke)
        t = re.sub(r"[ \t\xa0]+", " ", t)
        t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
        return t.strip()


def _pdf_text(pfad):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        leser = PdfReader(pfad)
        return "\n\n".join((s.extract_text() or "") for s in leser.pages).strip()
    except Exception:
        return ""


def _stuecke(text, laenge=1200, ueberlappung=150):
    """Absatzweise gefuellte Stuecke; ein Satz wird nicht mitten durchtrennt."""
    absaetze = [a.strip() for a in re.split(r"\n\s*\n", text) if a.strip()]
    stuecke, jetzt = [], ""
    for a in absaetze:
        if len(jetzt) + len(a) + 2 <= laenge:
            jetzt = (jetzt + "\n\n" + a).strip()
        else:
            if jetzt:
                stuecke.append(jetzt)
            if len(a) <= laenge:
                jetzt = (stuecke[-1][-ueberlappung:] + "\n\n" + a).strip() if stuecke else a
            else:
                for i in range(0, len(a), laenge - ueberlappung):
                    stuecke.append(a[i:i + laenge])
                jetzt = ""
    if jetzt:
        stuecke.append(jetzt)
    return stuecke


def _ein_dokument(e, laenge, ueberlappung, aus):
    """Ein geladenes Dokument in Text und Stuecke verwandeln.

    Gibt (Text geschrieben?, Zahl der Stuecke, pypdf fehlt?) zurueck.
    """
    quelle = _pfad("dateien", e["pfad"])
    if not os.path.exists(quelle):
        return False, 0, False
    endung = os.path.splitext(quelle)[1].lower()
    if endung == ".pdf":
        t = _pdf_text(quelle)
        if t is None:
            return False, 0, True
    elif endung in (".htm", ".html"):
        p = _NurText()
        p.feed(open(quelle, "rb").read().decode("utf-8", "replace"))
        t = p.text()
    elif endung == ".txt":
        t = open(quelle, encoding="utf-8", errors="replace").read()
    else:
        return False, 0, False
    if not t or len(t) < 200:
        return False, 0, False

    ziel = _pfad("text", os.path.splitext(e["pfad"])[0] + ".txt")
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    open(ziel, "w", encoding="utf-8").write(t)

    kopf = "%s (%s) · %s · Quartal %s · eingereicht %s" % (
        e.get("firma"), e["ticker"], e.get("art") or e.get("form"),
        e.get("quartal_ende") or "?", e.get("eingereicht") or "?")
    n = 0
    for i, s in enumerate(_stuecke(t, laenge, ueberlappung)):
        aus.write(json.dumps({
            "id": "%s|%s|%d" % (e["ticker"], e["pfad"].replace("\\", "/"), i),
            "ticker": e["ticker"], "firma": e.get("firma"),
            "quartal_ende": e.get("quartal_ende"), "eingereicht": e.get("eingereicht"),
            "form": e.get("form"), "art": e.get("art"), "quelle": e["url"],
            "stueck": i, "text": kopf + "\n\n" + s,
        }, ensure_ascii=False) + "\n")
        n += 1
    return True, n, False


def text(args):
    protokoll = _pfad("geladen.jsonl")
    if not os.path.exists(protokoll):
        sys.exit("Nichts geladen. Erst 'laden' laufen lassen.")
    geladen = {}
    for z in open(protokoll, encoding="utf-8"):
        e = json.loads(z)
        if e.get("status") == "ok":
            geladen[e["url"]] = e

    os.makedirs(_pfad("text"), exist_ok=True)
    ohne_pypdf = 0
    aus = open(_pfad("stuecke.jsonl"), "w", encoding="utf-8")
    n_dok = n_stueck = 0
    for e in sorted(geladen.values(), key=lambda x: (x["ticker"], x.get("eingereicht") or "")):
        ok, n, fehlt = _ein_dokument(e, args.laenge, args.ueberlappung, aus)
        ohne_pypdf += 1 if fehlt else 0
        n_dok += 1 if ok else 0
        n_stueck += n
    aus.close()

    # Die Zahlen der Seite als eigene, saubere Saetze. Sie sind das Rueckgrat:
    # kurz, vollstaendig und ohne Extraktionsrauschen.
    D, _ = daten_der_seite()
    with open(_pfad("kennzahlen.jsonl"), "w", encoding="utf-8") as f:
        for sym, e in D["firmen"].items():
            w = e.get("waehrung_heim") or e.get("waehrung")
            for q in e["quartale"]:
                teile = ["%s (%s), Quartal endend %s" % (e["name"], sym, q["ende"])]
                for feld, wort in (("umsatz", "Umsatz"), ("brutto", "Bruttoergebnis"),
                                   ("operativ", "operatives Ergebnis"), ("netto", "Nettogewinn")):
                    if q.get(feld) is not None:
                        teile.append("%s %.4g %s" % (wort, q[feld], w))
                for feld, wort in (("eps", "Gewinn je Aktie"),):
                    if q.get(feld) is not None:
                        teile.append("%s %.4g %s" % (wort, q[feld], w))
                for feld, wort in (("bruttomarge", "Bruttomarge"), ("operativmarge", "operative Marge"),
                                   ("nettomarge", "Nettomarge"), ("umsatz_yoy", "Umsatzwachstum zum Vorjahr")):
                    if q.get(feld) is not None:
                        teile.append("%s %.1f Prozent" % (wort, q[feld]))
                teile.append("Quelle: %s" % q.get("quelle", "?"))
                f.write(json.dumps({
                    "id": "%s|%s" % (sym, q["ende"]), "ticker": sym, "firma": e["name"],
                    "quartal_ende": q["ende"], "rolle": e.get("rolle"), "waehrung": w,
                    "text": ", ".join(teile) + ".", "zahlen": q,
                }, ensure_ascii=False) + "\n")

    print("Text aus %d Dokumenten, %d Stuecke -> %s" % (n_dok, n_stueck, _pfad("stuecke.jsonl")))
    print("Kennzahlen je Quartal -> %s" % _pfad("kennzahlen.jsonl"))
    if ohne_pypdf:
        print("%d PDF uebersprungen, weil pypdf fehlt:  pip install pypdf" % ohne_pypdf)


# ------------------------------------------------------------------ einbetten

# Der Einbettungsserver ist ein zweiter llama-server auf einem eigenen Port,
# damit der Chatserver auf 8080 ungestoert bleibt. Siehe start-embed.ps1.
EMBED_URL = os.environ.get("EMBED_URL", "http://127.0.0.1:8081/v1/embeddings")


def _vektoren_pfade():
    return (_pfad("vektoren", "vektoren.f32"),
            _pfad("vektoren", "vektoren.jsonl"),
            _pfad("vektoren", "meta.json"))


def _einbetten_roh(texte):
    """Eine Fuhre Texte an den lokalen Server, normierte Vektoren zurueck.

    Kein Takt und keine Wiederholung: das laeuft ueber die Loopback-Schnittstelle,
    ein Fehler hier ist ein Serverproblem und soll sofort auffallen.
    """
    import numpy as np
    last = json.dumps({"input": texte, "model": "lokal"}).encode("utf-8")
    anfrage = urllib.request.Request(
        EMBED_URL, data=last,
        headers={"Content-Type": "application/json", "User-Agent": "AI_Companys/1.0"})
    with urllib.request.urlopen(anfrage, timeout=600) as antwort:
        d = json.loads(antwort.read())
    raus = []
    for e in d["data"]:
        v = e["embedding"]
        # Manche Builds liefern je Eingabe eine Liste von Token-Vektoren statt
        # eines gepoolten; dann wird hier gemittelt.
        v = np.array(v, dtype="float32")
        if v.ndim == 2:
            v = v.mean(axis=0)
        norm = float(np.linalg.norm(v))
        raus.append(v / norm if norm else v)
    return np.vstack(raus)


def _quellzeilen(args):
    """Was eingebettet wird: die Dokumentstuecke und die Kennzahlensaetze."""
    quellen = [("stuecke.jsonl", "dokument")]
    if not args.ohne_kennzahlen:
        quellen.append(("kennzahlen.jsonl", "kennzahl"))
    for name, art in quellen:
        p = _pfad(name)
        if not os.path.exists(p):
            continue
        for z in open(p, encoding="utf-8"):
            z = z.strip()
            if not z:
                continue
            e = json.loads(z)
            e["quellart"] = art
            yield e


def einbetten(args):
    import numpy as np
    vek, index, meta = _vektoren_pfade()
    os.makedirs(os.path.dirname(vek), exist_ok=True)

    fertig = set()
    if os.path.exists(index):
        for z in open(index, encoding="utf-8"):
            try:
                fertig.add(json.loads(z)["id"])
            except Exception:
                pass

    offen = [e for e in _quellzeilen(args) if e["id"] not in fertig]
    print("%d Stuecke insgesamt neu, %d bereits eingebettet" % (len(offen), len(fertig)))
    if not offen:
        return
    if args.grenze:
        offen = offen[: args.grenze]
        print("auf %d begrenzt (--grenze)" % len(offen))

    dim = None
    if os.path.exists(meta):
        dim = json.load(open(meta, encoding="utf-8")).get("dim")

    t0 = time.time()
    n = 0
    with open(vek, "ab") as fv, open(index, "a", encoding="utf-8") as fi:
        for i in range(0, len(offen), args.fuhre):
            teil = offen[i:i + args.fuhre]
            try:
                m = _einbetten_roh([e["text"] for e in teil])
            except Exception as f:
                print("Abbruch bei Stueck %d: %s" % (i, f))
                print("Der Lauf ist wiederholbar - schon Eingebettetes bleibt liegen.")
                break
            if dim is None:
                dim = int(m.shape[1])
                json.dump({"dim": dim, "url": EMBED_URL, "normiert": True},
                          open(meta, "w", encoding="utf-8"), indent=1)
            elif m.shape[1] != dim:
                sys.exit("Vektorlaenge %d passt nicht zu den vorhandenen %d - "
                         "anderes Modell? Dann vektoren/ loeschen und neu einbetten."
                         % (m.shape[1], dim))
            fv.write(m.astype("float32").tobytes())
            for e in teil:
                fi.write(json.dumps({
                    "id": e["id"], "ticker": e.get("ticker"), "firma": e.get("firma"),
                    "quartal_ende": e.get("quartal_ende"), "eingereicht": e.get("eingereicht"),
                    "form": e.get("form"), "art": e.get("art"), "quelle": e.get("quelle"),
                    "quellart": e["quellart"], "text": e["text"][:400],
                }, ensure_ascii=False) + "\n")
            fv.flush()
            fi.flush()
            n += len(teil)
            if (i // args.fuhre) % 10 == 0 or n == len(offen):
                v = n / max(time.time() - t0, 0.001)
                rest = (len(offen) - n) / v if v else 0
                print("   %6d/%d  %.0f Stueck/s  noch etwa %d min"
                      % (n, len(offen), v, rest / 60))
    print("%d Vektoren mit %s Dimensionen -> %s" % (n, dim, vek))


def suchen(args):
    import numpy as np
    vek, index, meta = _vektoren_pfade()
    if not os.path.exists(vek):
        sys.exit("Keine Vektoren. Erst 'einbetten' laufen lassen.")
    dim = json.load(open(meta, encoding="utf-8"))["dim"]
    M = np.fromfile(vek, dtype="float32").reshape(-1, dim)
    zeilen = [json.loads(z) for z in open(index, encoding="utf-8") if z.strip()]
    if len(zeilen) != M.shape[0]:
        n = min(len(zeilen), M.shape[0])
        print("Hinweis: %d Vektoren, %d Indexzeilen - auf %d gekuerzt."
              % (M.shape[0], len(zeilen), n))
        M, zeilen = M[:n], zeilen[:n]

    frage = _einbetten_roh([args.frage])[0]
    aehnlich = M @ frage

    erlaubt = None
    if args.firma:
        erlaubt = {t.strip().upper() for t in args.firma.split(",")}
    treffer = []
    for i in np.argsort(-aehnlich):
        z = zeilen[i]
        if erlaubt and (z.get("ticker") or "").upper() not in erlaubt:
            continue
        if args.ab and (z.get("eingereicht") or z.get("quartal_ende") or "") < args.ab:
            continue
        treffer.append((float(aehnlich[i]), z))
        if len(treffer) >= args.top:
            break

    print("Frage: %s\n" % args.frage)
    for wert, z in treffer:
        kopf = "%.3f  %-8s %-9s %s" % (wert, z.get("ticker") or "?",
                                       z.get("quartal_ende") or "", z.get("art") or z.get("quellart"))
        print(kopf)
        text = " ".join((z.get("text") or "").split())
        print("        %s" % text[:240])
        if z.get("quelle"):
            print("        %s" % z["quelle"])
        print()


# ------------------------------------------------------------------- analyse

def _auszug(pfad, zeichen):
    """Anfang eines Dokuments, Leerraum zusammengezogen.

    Der Anfang genuegt: Pressemitteilungen stellen Umsatz, Ergebnis und Ausblick
    in die ersten Absaetze, und alles Weitere kostet nur Kontext.
    """
    if not os.path.exists(pfad):
        return ""
    t = open(pfad, encoding="utf-8", errors="replace").read()
    return re.sub(r"\n{3,}", "\n\n", t[:zeichen * 2]).strip()[:zeichen]


def _auffaelligkeiten(quartale):
    """Rechnerische Trendbrueche. Keine Deutung, nur Arithmetik.

    Das Modell soll spaeter beurteilen, was ein Knick bedeutet - finden soll ihn
    der Rechner, denn genau daran scheitern Sprachmodelle zuverlaessig.
    """
    q = [z for z in sorted(quartale, key=lambda z: z["ende"]) if z.get("umsatz")]
    raus = []
    if len(q) < 5:
        return raus

    def yoy(i):
        vor = q[i - 4]["umsatz"] if i >= 4 else None
        return (q[i]["umsatz"] / vor - 1) * 100 if vor else None

    w_jetzt, w_vor = yoy(len(q) - 1), yoy(len(q) - 2)
    if w_jetzt is not None and w_vor is not None:
        d = w_jetzt - w_vor
        if abs(d) >= 8:
            raus.append("Umsatzwachstum %s: %+.0f %% nach %+.0f %% im Vorquartal (%+.0f Punkte)"
                        % ("bricht" if d < 0 else "zieht an", w_jetzt, w_vor, d))
    if w_jetzt is not None and w_vor is not None and (w_jetzt < 0) != (w_vor < 0):
        raus.append("Vorzeichenwechsel beim Umsatzwachstum")

    for feld, wort in (("operativmarge", "operative Marge"), ("bruttomarge", "Bruttomarge")):
        werte = [(z["ende"], z[feld]) for z in q[-5:] if z.get(feld) is not None]
        if len(werte) >= 3:
            d = werte[-1][1] - werte[-2][1]
            if abs(d) >= 3:
                raus.append("%s %+.1f Punkte auf %.1f %%" % (wort, d, werte[-1][1]))

    j = q[-1]
    if j.get("netto") is not None and j.get("operativ"):
        ab = abs(j["netto"] - j["operativ"]) / abs(j["operativ"]) * 100
        if ab >= 25:
            raus.append("Nettoergebnis weicht %.0f %% vom operativen ab - betriebsfremde Posten "
                        "bestimmen den Gewinn" % ab)
    return raus


def _aehnliche_stellen(text, sym, vor_datum, anzahl=3):
    """Wo dieselbe Firma frueher schon einmal aehnlich geklungen hat.

    Braucht die Vektoren; fehlen sie, faellt die Analyse still auf die
    Vorquartalsdokumente zurueck.
    """
    vek, index, meta = _vektoren_pfade()
    if not (os.path.exists(vek) and os.path.exists(meta)):
        return []
    try:
        import numpy as np
        dim = json.load(open(meta, encoding="utf-8"))["dim"]
        M = np.fromfile(vek, dtype="float32").reshape(-1, dim)
        zeilen = [json.loads(z) for z in open(index, encoding="utf-8") if z.strip()]
        n = min(len(zeilen), M.shape[0])
        M, zeilen = M[:n], zeilen[:n]
        frage = _einbetten_roh([text[:1500]])[0]
        werte = M @ frage
        raus = []
        for i in np.argsort(-werte):
            z = zeilen[i]
            if (z.get("ticker") or "") != sym:
                continue
            if (z.get("eingereicht") or "9999") >= vor_datum:
                continue
            raus.append((float(werte[i]), z))
            if len(raus) >= anzahl:
                break
        return raus
    except Exception:
        return []


def analyse(args):
    tag = args.tag or date.today().isoformat()
    protokoll = _pfad("geladen.jsonl")
    if not os.path.exists(protokoll):
        sys.exit("Nichts geladen.")

    alle = []
    for z in open(protokoll, encoding="utf-8"):
        try:
            alle.append(json.loads(z))
        except Exception:
            pass
    neu = [e for e in alle if e.get("status") == "ok" and e.get("geladen_am") == tag]
    if not neu:
        print("Fuer %s ist nichts hereingekommen - keine Analyse." % tag)
        return

    D, _ = daten_der_seite()
    F = D["firmen"]
    nach_firma = {}
    for e in neu:
        nach_firma.setdefault(e["ticker"], []).append(e)

    teile = ["# Beleglage %s" % tag, "",
             "Neue Einreichungen bei %d Firmen. Zahlen aus dem Datensatz vom %s; "
             "die Auszuege stammen aus den heute eingegangenen Dokumenten."
             % (len(nach_firma), D.get("stand", "?")), ""]

    for sym in sorted(nach_firma):
        e0 = F.get(sym, {})
        teile.append("## %s — %s" % (sym, e0.get("name", sym)))
        teile.append("")

        q = sorted(e0.get("quartale", []), key=lambda z: z["ende"])[-6:]
        if q:
            w = e0.get("waehrung_heim") or e0.get("waehrung") or ""
            teile.append("| Quartal | Umsatz | operativ | netto | op. Marge |")
            teile.append("|---|---:|---:|---:|---:|")
            for z in q:
                f = lambda v: ("%.3g" % v) if isinstance(v, (int, float)) else "—"
                teile.append("| %s | %s | %s | %s | %s |" % (
                    z["ende"], f(z.get("umsatz")), f(z.get("operativ")), f(z.get("netto")),
                    ("%.1f %%" % z["operativmarge"]) if z.get("operativmarge") is not None else "—"))
            teile.append("")
            teile.append("Waehrung: %s" % (w or "unbekannt"))
            teile.append("")

        auf = _auffaelligkeiten(e0.get("quartale", []))
        if auf:
            teile.append("**Rechnerisch auffaellig:**")
            for a in auf:
                teile.append("- %s" % a)
            teile.append("")

        for e in sorted(nach_firma[sym], key=lambda x: x.get("eingereicht") or ""):
            teile.append("### Neu: %s · %s · %s" % (e.get("eingereicht"), e.get("form"), e.get("art")))
            teile.append(e["url"])
            teile.append("")
            txt = _auszug(_pfad("text", os.path.splitext(e["pfad"])[0] + ".txt"), args.zeichen)
            if txt:
                teile.append("```")
                teile.append(txt)
                teile.append("```")
                teile.append("")
                for wert, z in _aehnliche_stellen(txt, sym, e.get("eingereicht") or tag):
                    teile.append("*Frueher aehnlich (%.2f, %s, %s):* %s"
                                 % (wert, z.get("quartal_ende") or "?", z.get("art") or "",
                                    " ".join((z.get("text") or "").split())[:300]))
                    teile.append("")

    paket = "\n".join(teile) + "\n"
    os.makedirs(_pfad("analyse"), exist_ok=True)
    p_paket = _pfad("analyse", tag + "-beleglage.md")
    open(p_paket, "w", encoding="utf-8").write(paket)
    print("Beleglage: %s  (%d Zeichen, %d Firmen)" % (p_paket, len(paket), len(nach_firma)))

    befehl = args.befehl or os.environ.get("ANALYSE_BEFEHL", "")
    if not befehl:
        print("Kein Analysebefehl gesetzt - die Beleglage liegt bereit, die Deutung fehlt.")
        print("Beispiel:  set ANALYSE_BEFEHL=claude -p")
        return

    import subprocess
    auftrag = (
        "Du bekommst die Beleglage eines Tages: je Firma die letzten Quartalszahlen, "
        "rechnerisch gefundene Auffaelligkeiten und Auszuege aus heute eingegangenen "
        "Einreichungen.\n\n"
        "Schreibe daraus eine knappe Lage auf Deutsch:\n"
        "1. Was ist neu, das vorher nicht bekannt war.\n"
        "2. Welcher Trend setzt sich fort - mit der Zahl, die das stuetzt.\n"
        "3. Wo bricht ein Trend, und was im Text erklaert den Bruch.\n"
        "4. Was widerspricht sich zwischen Zahl und Formulierung.\n\n"
        "Regeln: Keine Zahl nennen, die nicht in der Beleglage steht. Wo der Text "
        "nichts hergibt, schreibe das, statt zu vermuten. Keine Anlageberatung, "
        "keine Empfehlungen. Nenne bei jeder Aussage die Firma.\n\n"
        "---\n\n" + paket
    )
    print("Deutung laeuft: %s" % befehl)
    try:
        erg = subprocess.run(befehl, shell=True, input=auftrag, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=1800)
    except Exception as f:
        print("Analysebefehl fehlgeschlagen: %s" % f)
        return
    if erg.returncode != 0 or not (erg.stdout or "").strip():
        print("Analysebefehl ohne Ergebnis (Code %s): %s" % (erg.returncode, (erg.stderr or "")[:300]))
        return
    p_lage = _pfad("analyse", tag + ".md")
    open(p_lage, "w", encoding="utf-8").write(
        "# Lage %s\n\n*Maschinell erzeugt aus den an diesem Tag eingegangenen Einreichungen. "
        "Zahlen koennen Extraktionsfehler enthalten; die Quelle steht in der Beleglage. "
        "Keine Anlageberatung.*\n\n" % tag + erg.stdout.strip() + "\n")
    print("Lage: %s" % p_lage)


# ----------------------------------------------------------- veroeffentlichen

# Veroeffentlicht wird nie aus dem Arbeitsverzeichnis, sondern aus einem eigenen
# Arbeitsbaum auf einem eigenen Zweig. Der Lauf um fuenf Uhr weiss nicht, woran
# gerade gearbeitet wird; er darf weder den Zweig wechseln noch ungesicherte
# Aenderungen anfassen. git worktree gibt ihm ein zweites Verzeichnis auf
# denselben Objektspeicher - eigener Zweig, eigener Stand, kein Einfluss.
ZWEIG = os.environ.get("BERICHTE_ZWEIG", "berichte-automatik")


def _git(pfad, *args, pruefen=True):
    import subprocess
    erg = subprocess.run(["git", "-C", pfad] + list(args), capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    if pruefen and erg.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), (erg.stderr or erg.stdout).strip()[:300]))
    return (erg.stdout or "").strip()


def _arbeitsbaum(zweig):
    """Das zweite Verzeichnis auf dem Veroeffentlichungszweig, notfalls anlegen."""
    baum = _pfad("veroeffentlichung")
    if os.path.exists(os.path.join(baum, ".git")):
        return baum
    os.makedirs(os.path.dirname(baum), exist_ok=True)
    vorhanden = _git(WURZEL, "branch", "--list", zweig)
    if vorhanden:
        _git(WURZEL, "worktree", "add", baum, zweig)
    else:
        # Neuer Zweig, vom Stand des Fernzweigs main - unabhaengig davon, woran
        # im Hauptverzeichnis gerade gearbeitet wird.
        basis = "origin/main" if _git(WURZEL, "branch", "-r", "--list", "origin/main") else "main"
        _git(WURZEL, "worktree", "add", "-b", zweig, baum, basis)
    return baum


def veroeffentlichen(args):
    tag = args.tag or date.today().isoformat()
    quelle = _pfad("analyse", tag + ".md")
    if not os.path.exists(quelle):
        sys.exit("Keine gedeutete Lage fuer %s. Erst 'analyse' mit gesetztem "
                 "Analysebefehl laufen lassen; die reine Beleglage wird nicht "
                 "veroeffentlicht." % tag)

    zweig = args.zweig or ZWEIG
    if zweig in ("main", "master"):
        sys.exit("Auf %s wird von hier aus nicht veroeffentlicht. Dafuer ist der "
                 "Umweg ueber einen Pull Request da." % zweig)

    baum = _arbeitsbaum(zweig)
    ordner = os.path.join(baum, "lage")
    os.makedirs(ordner, exist_ok=True)
    ziel = os.path.join(ordner, tag + ".md")
    inhalt = open(quelle, encoding="utf-8").read()
    open(ziel, "w", encoding="utf-8").write(inhalt)

    # Uebersicht neu schreiben, neueste zuerst.
    tage = sorted((f[:-3] for f in os.listdir(ordner)
                   if re.match(r"\d{4}-\d{2}-\d{2}\.md$", f)), reverse=True)
    zeilen = ["# Tageslage", "",
              "Maschinell erzeugte Zusammenfassungen der Quartalsberichte entlang",
              "Nvidias Lieferkette. Je Tag eine Datei, erzeugt aus den an diesem Tag",
              "bei der SEC eingegangenen Einreichungen.", "",
              "Keine Anlageberatung. Zahlen koennen Extraktionsfehler enthalten.", ""]
    for t in tage:
        erste = ""
        for z in open(os.path.join(ordner, t + ".md"), encoding="utf-8"):
            z = z.strip()
            if z and not z.startswith("#") and not z.startswith("*"):
                erste = z[:120]
                break
        zeilen.append("- [%s](%s.md)%s" % (t, t, (" — " + erste) if erste else ""))
    open(os.path.join(ordner, "index.md"), "w", encoding="utf-8").write("\n".join(zeilen) + "\n")

    if args.nur_pruefen:
        print("Wuerde schreiben: %s\nund %s/index.md\nZweig: %s" % (ziel, ordner, zweig))
        return

    _git(baum, "add", "lage")
    if not _git(baum, "status", "--porcelain"):
        print("Nichts zu committen - die Lage vom %s steht schon auf %s." % (tag, zweig))
        return
    _git(baum, "commit", "-m", "Tageslage %s" % tag)
    print("Committet auf %s" % zweig)
    if args.ohne_push:
        print("Ohne Push (--ohne-push). Von Hand:  git -C %s push -u origin %s" % (baum, zweig))
        return
    try:
        _git(baum, "push", "-u", "origin", zweig)
        print("Gepusht nach origin/%s" % zweig)
    except Exception as f:
        print("Push fehlgeschlagen: %s" % f)
        print("Der Commit liegt in %s und laesst sich spaeter nachschieben." % baum)


# ------------------------------------------------------------------ taeglich

def _stand_lesen():
    p = _pfad("stand.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def taeglich(args):
    """Ein Lauf: nachsehen, was neu eingereicht wurde, holen, aufbereiten.

    Zustandsbehaftet statt datumsbehaftet: gemerkt wird je Firma die letzte
    gesehene Einreichung, nicht wann der Lauf zuletzt lief. Stand der Rechner
    drei Wochen aus, holt der naechste Lauf die drei Wochen nach, ohne dass
    jemand etwas nachstellen muss.
    """
    D, _ = daten_der_seite()
    F = D["firmen"]
    stand = _stand_lesen()
    bekannt = set()
    for name in ("arbeitsliste.jsonl", "geladen.jsonl"):
        p = _pfad(name)
        if os.path.exists(p):
            for z in open(p, encoding="utf-8"):
                try:
                    bekannt.add(json.loads(z)["url"])
                except Exception:
                    pass

    verzeichnis = None
    neu = []
    fehler = []
    for sym, e in F.items():
        eintrag = stand.setdefault(sym, {})
        cik = eintrag.get("cik") or e.get("cik")
        if not cik:
            if verzeichnis is None:
                try:
                    verzeichnis = _cik_verzeichnis()
                except Exception as f:
                    fehler.append(("Ticker-Verzeichnis", str(f)[:120]))
                    verzeichnis = {}
            cik = verzeichnis.get(sym.upper()) or verzeichnis.get(str(e.get("symbol", "")).upper())
        if not cik:
            eintrag["cik"] = None
            continue
        cik = str(cik).zfill(10)
        eintrag["cik"] = cik
        # Fuenf Tage Rueckgriff: die SEC stellt Einreichungen gelegentlich
        # nach, und doppelt gesehen kostet nur eine Anfrage.
        seit = eintrag.get("letzte_einreichung") or args.ab
        if seit > args.ab:
            j, m, t = (int(x) for x in seit.split("-"))
            seit = date(j, m, t).fromordinal(date(j, m, t).toordinal() - 5).isoformat()
        try:
            _, zeilen = _einreichungen(cik, nur_neue=True)
        except Exception as f:
            fehler.append((sym, str(f)[:120]))
            continue
        passend = [z for z in zeilen
                   if z.get("form") in FORMULARE and (z.get("filingDate") or "") >= seit]
        for z in passend:
            try:
                docs = _filing_dokumente(cik, z["accessionNumber"], z.get("primaryDocument"), z.get("form", ""))
            except Exception as f:
                fehler.append((sym + " " + z["accessionNumber"], str(f)[:120]))
                continue
            for d in docs:
                if d["url"] in bekannt:
                    continue
                bekannt.add(d["url"])
                eintr = {
                    "ticker": sym, "firma": e.get("name", sym),
                    "quartal_ende": z.get("reportDate"), "eingereicht": z.get("filingDate"),
                    "form": z.get("form"), "art": d["art"], "url": d["url"],
                    "herkunft": "edgar", "zugang": z["accessionNumber"],
                }
                eintr["pfad"] = os.path.join(
                    sym, (eintr["quartal_ende"] or eintr["eingereicht"] or "ohne-datum"),
                    _sicher(os.path.basename(urlparse(d["url"]).path) or "dokument"))
                neu.append(eintr)
        if passend:
            eintrag["letzte_einreichung"] = max(z["filingDate"] for z in passend)

    # Anhaengen, laden, aufbereiten - nur das Neue.
    geladen = []
    if neu and not args.nur_pruefen:
        with open(_pfad("arbeitsliste.jsonl"), "a", encoding="utf-8") as f:
            for e in neu:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        with open(_pfad("geladen.jsonl"), "a", encoding="utf-8") as mit:
            for e in neu:
                ziel = _pfad("dateien", e["pfad"])
                os.makedirs(os.path.dirname(ziel), exist_ok=True)
                try:
                    roh, typ, _ = hole(e["url"])
                    open(ziel, "wb").write(roh)
                    e = dict(e, status="ok", bytes=len(roh), content_type=typ,
                             sha256=hashlib.sha256(roh).hexdigest(),
                             geladen_am=date.today().isoformat())
                    geladen.append(e)
                except Exception as f:
                    e = dict(e, status="fehler", fehler=str(f)[:200])
                    fehler.append((e["ticker"], e["url"][-60:]))
                mit.write(json.dumps(e, ensure_ascii=False) + "\n")

        with open(_pfad("stuecke.jsonl"), "a", encoding="utf-8") as aus:
            for e in geladen:
                _ein_dokument(e, args.laenge, args.ueberlappung, aus)

    if not args.nur_pruefen:
        json.dump(stand, open(_pfad("stand.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # Bericht des Laufs: eine Datei je Tag, damit sich nachlesen laesst, was
    # wann hereinkam, ohne das Protokoll zu durchsuchen.
    heute = date.today().isoformat()
    os.makedirs(_pfad("laeufe"), exist_ok=True)
    zeilen = ["# Lauf %s" % heute, ""]
    if neu:
        zeilen.append("%d neue Dokumente, %d geladen." % (len(neu), len(geladen)))
        zeilen.append("")
        nach_firma = {}
        for e in neu:
            nach_firma.setdefault(e["ticker"], []).append(e)
        for sym in sorted(nach_firma):
            zeilen.append("## %s" % sym)
            for e in sorted(nach_firma[sym], key=lambda x: x["eingereicht"] or ""):
                zeilen.append("- %s · %s · %s · %s" %
                              (e["eingereicht"], e["form"], e["art"], e["url"]))
            zeilen.append("")
    else:
        zeilen.append("Keine neuen Einreichungen.")
        zeilen.append("")
    if fehler:
        zeilen.append("## Fehler")
        for wo, was in fehler[:30]:
            zeilen.append("- %s: %s" % (wo, was))
    bericht = "\n".join(zeilen) + "\n"
    open(_pfad("laeufe", heute + ".md"), "w", encoding="utf-8").write(bericht)
    print(bericht)


# -------------------------------------------------------------------- status

def status(args):
    liste = _arbeitsliste_lesen() if os.path.exists(_pfad("arbeitsliste.jsonl")) else []
    protokoll = _pfad("geladen.jsonl")
    geladen = {}
    if os.path.exists(protokoll):
        for z in open(protokoll, encoding="utf-8"):
            e = json.loads(z)
            geladen[e["url"]] = e
    ok = [e for e in geladen.values() if e.get("status") == "ok"]
    fehler = [e for e in geladen.values() if e.get("status") != "ok"]
    print("Arbeitsliste: %d Dokumente, %d Firmen" % (len(liste), len({e["ticker"] for e in liste})))
    print("geladen: %d (%.1f MB), Fehler: %d" % (len(ok), sum(e.get("bytes", 0) for e in ok) / 1e6, len(fehler)))
    je = {}
    for e in liste:
        je.setdefault(e["ticker"], [0, 0])[0] += 1
    for e in ok:
        je.setdefault(e["ticker"], [0, 0])[1] += 1
    print("\n%-10s %6s %6s" % ("Ticker", "Liste", "da"))
    for t in sorted(je):
        print("%-10s %6d %6d" % (t, je[t][0], je[t][1]))
    if fehler:
        print("\nFehler:")
        for e in fehler[:20]:
            print("   %-10s %s  %s" % (e["ticker"], e["url"][:80], e.get("fehler", "")[:60]))


# ---------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    u = p.add_subparsers(dest="befehl", required=True)

    s = u.add_parser("sammeln", help="Arbeitsliste aus Seitenlinks und EDGAR bauen")
    s.add_argument("--ab", default="2021-01-01", help="nur Einreichungen ab diesem Datum (Standard 2021-01-01)")
    s.add_argument("--grenze", type=int, default=0, help="hoechstens so viele Einreichungen je Firma")
    s.add_argument("--nur-kuratiert", action="store_true", help="ohne EDGAR, nur die Links aus der Seite")
    s.set_defaults(f=sammeln)

    l = u.add_parser("laden", help="Dokumente herunterladen, wiederholbar")
    l.add_argument("--mit-audio", action="store_true", help="auch mp3 der Earnings Calls")
    l.add_argument("--firma", default="", help="nur diese Ticker, mit Komma getrennt")
    l.set_defaults(f=laden)

    t = u.add_parser("text", help="Text herausziehen und in Stuecke schneiden")
    t.add_argument("--laenge", type=int, default=1200, help="Zeichen je Stueck")
    t.add_argument("--ueberlappung", type=int, default=150, help="Zeichen Ueberlappung")
    t.set_defaults(f=text)

    eb = u.add_parser("einbetten", help="Stuecke am lokalen Server in Vektoren verwandeln")
    eb.add_argument("--fuhre", type=int, default=16, help="Stuecke je Anfrage")
    eb.add_argument("--grenze", type=int, default=0, help="hoechstens so viele Stuecke diesmal")
    eb.add_argument("--ohne-kennzahlen", action="store_true", help="nur Dokumentstuecke, keine Kennzahlensaetze")
    eb.set_defaults(f=einbetten)

    su = u.add_parser("suchen", help="in den Vektoren suchen")
    su.add_argument("frage", help="wonach gesucht wird")
    su.add_argument("--top", type=int, default=8, help="Zahl der Treffer")
    su.add_argument("--firma", default="", help="nur diese Ticker, mit Komma getrennt")
    su.add_argument("--ab", default="", help="nur Quartale ab diesem Datum")
    su.set_defaults(f=suchen)

    an = u.add_parser("analyse", help="Beleglage des Tages bauen und deuten lassen")
    an.add_argument("--tag", default="", help="Datum JJJJ-MM-TT, Standard heute")
    an.add_argument("--zeichen", type=int, default=4000, help="Zeichen Auszug je neuem Dokument")
    an.add_argument("--befehl", default="", help="Befehl, der die Beleglage deutet (sonst ANALYSE_BEFEHL)")
    an.set_defaults(f=analyse)

    vo = u.add_parser("veroeffentlichen", help="Tageslage auf den Veroeffentlichungszweig committen")
    vo.add_argument("--tag", default="", help="Datum JJJJ-MM-TT, Standard heute")
    vo.add_argument("--zweig", default="", help="Zielzweig, Standard berichte-automatik")
    vo.add_argument("--ohne-push", action="store_true", help="nur committen, nicht pushen")
    vo.add_argument("--nur-pruefen", action="store_true", help="nur zeigen, was passieren wuerde")
    vo.set_defaults(f=veroeffentlichen)

    tg = u.add_parser("taeglich", help="nachsehen, was neu ist, holen und aufbereiten")
    tg.add_argument("--ab", default="2021-01-01", help="Bodendatum beim allerersten Lauf")
    tg.add_argument("--laenge", type=int, default=1200, help="Zeichen je Stueck")
    tg.add_argument("--ueberlappung", type=int, default=150, help="Zeichen Ueberlappung")
    tg.add_argument("--nur-pruefen", action="store_true", help="nur melden, nichts laden oder merken")
    tg.set_defaults(f=taeglich)

    st = u.add_parser("status", help="Ueberblick")
    st.set_defaults(f=status)

    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
