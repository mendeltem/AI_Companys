# SK hynix: taeglicher Handel nach Anlegergruppe von Naver holen und als CSV
# ablegen. Naver gibt die KRX-Zahlen wieder (Tier 2): Auslaenderanteil an den
# gelisteten Aktien, Nettokauf in Stueck fuer Auslaender, Institutionen und
# Privatanleger, Schlusskurs, Volumen.
#
# Netz noetig (m.stock.naver.com). KRX selbst verlangt fuer die
# Datenschnittstelle seit 2025/26 ein Konto, deshalb Naver.
#
# Aufruf, Arbeitsverzeichnis egal:
#   python3 -I /home/user/AI_Companys/speicher_analysen/rechnungen/09_aktionaere_holen.py

import csv
import json
import time
import urllib.request
from pathlib import Path

P = Path(__file__).resolve().parent.parent
ZIEL = P / "daten" / "skhynix_naver_handel.csv"
AB = "20230901"

def hole(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))

def zahl(s):
    if s in (None, "", "-"):
        return None
    return float(str(s).replace(",", "").replace("+", "").replace("%", ""))

zeilen = {}
datum = time.strftime("%Y%m%d", time.localtime(time.time() + 86400))
for seite in range(80):
    z = hole(f"https://m.stock.naver.com/api/stock/000660/trend?pageSize=60&bizdate={datum}")
    if not z:
        break
    for r in z:
        zeilen[r["bizdate"]] = r
    datum = z[-1]["bizdate"]
    print(seite, z[0]["bizdate"], z[-1]["bizdate"])
    if datum < AB:
        break
    time.sleep(0.7)

# Der juengste Tag hat in der Trendliste oft noch keinen Anteil; die
# Uebersichtsseite traegt ihn.
uebersicht = hole("https://m.stock.naver.com/api/stock/000660/integration")
for r in uebersicht.get("dealTrendInfos", []):
    alt = zeilen.setdefault(r["bizdate"], {})
    for feld, wert in r.items():
        if alt.get(feld) in (None, "", "-"):
            alt[feld] = wert

with open(ZIEL, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["datum", "schluss_krw", "auslaender_anteil_pct", "netto_auslaender", "netto_institutionen",
                "netto_privat", "volumen", "quelle"])
    for d in sorted(zeilen):
        if d < AB:
            continue
        r = zeilen[d]
        w.writerow([f"{d[:4]}-{d[4:6]}-{d[6:]}", zahl(r.get("closePrice")), zahl(r.get("foreignerHoldRatio")),
                    zahl(r.get("foreignerPureBuyQuant")), zahl(r.get("organPureBuyQuant")),
                    zahl(r.get("individualPureBuyQuant")), zahl(r.get("accumulatedTradingVolume")),
                    "Naver m.stock (KRX-Daten), Tier 2"])
print("Zeilen:", len([d for d in zeilen if d >= AB]), "->", ZIEL)
