# Quartale von Nvidia, SK hynix, Samsung und Micron aus der eigenen Seite holen
# und als CSV ablegen. Die Seite ist keine Quelle (Wiki-Regel
# own-visualisation-is-not-a-source): jede Zeile traegt deshalb die Quelle, die
# in der Seite steht, und einen Pruefstatus. XBRL-Zeilen sind maschinell aus
# der Einreichung gelesen, Handzeilen sind bis zur Gegenpruefung ungeprueft.
#
# KRW wird mit einem festen Kurs umgerechnet (daten/parameter.csv,
# kurs_krw_usd). Fester Kurs heisst: Wachstumsraten in USD sind dieselben wie
# in KRW. Mit Quartalskursen wuerde die Waehrung in die Wachstumsrate laufen.

import csv
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent.parent
SEITE = P.parent / "nvidia-oekosystem.html"
ZIEL = P / "daten" / "quartale.csv"

par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}
krw_je_usd = par["kurs_krw_usd"]

s = SEITE.read_text(encoding="utf-8")
m = re.search(r'<script id="daten" type="application/json">(.*?)</script>', s, re.S)
D = json.loads(m.group(1))
print("Stand der Seite:", D["stand"], "| Kurse:", D["stand_kurse"])

FIRMEN = ["NVDA", "SKHYNIX", "SAMSUNG", "MU"]
zeilen = []
for k in FIRMEN:
    f = D["firmen"][k]
    waehrung = f["waehrung"]
    zu_usd = 1.0 if waehrung == "USD" else 1.0 / krw_je_usd
    for q in f["quartale"]:
        if q["ende"] < "2022-01-01":
            continue
        quelle = q.get("quelle") or ""
        if quelle == "SEC XBRL":
            pruef = "maschinell aus XBRL"
        else:
            pruef = "von Hand aus Bericht, nicht gegengeprueft"
        umsatz = q.get("umsatz")
        operativ = q.get("operativ")
        netto = q.get("netto")
        zeilen.append({
            "firma": k,
            "ende": q["ende"],
            "waehrung": waehrung,
            "umsatz_mrd": round(umsatz / 1e9, 3) if umsatz is not None else "",
            "operativ_mrd": round(operativ / 1e9, 3) if operativ is not None else "",
            "netto_mrd": round(netto / 1e9, 3) if netto is not None else "",
            "umsatz_mrd_usd": round(umsatz * zu_usd / 1e9, 2) if umsatz is not None else "",
            "operativ_mrd_usd": round(operativ * zu_usd / 1e9, 2) if operativ is not None else "",
            "netto_mrd_usd": round(netto * zu_usd / 1e9, 2) if netto is not None else "",
            "quelle": quelle,
            "pruefstatus": pruef,
            "link": q.get("link") or "",
        })

zeilen.sort(key=lambda z: (z["firma"], z["ende"]))
with open(ZIEL, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(zeilen[0].keys()))
    w.writeheader()
    w.writerows(zeilen)

for k in FIRMEN:
    n = sum(1 for z in zeilen if z["firma"] == k)
    letzte = [z for z in zeilen if z["firma"] == k][-1]
    print(f"{k:8s} {n:2d} Quartale, letztes {letzte['ende']}: Umsatz {letzte['umsatz_mrd_usd']} Mrd USD, "
          f"operativ {letzte['operativ_mrd_usd']}, netto {letzte['netto_mrd_usd']} ({letzte['pruefstatus']})")
print("geschrieben:", ZIEL)

# Marktkapitalisierung SK hynix zum Kurs der Seite
f = D["firmen"]["SKHYNIX"]
mk_krw = f["kurs"] * f["aktien_zahl"]
print(f"SK hynix Kurs {f['kurs']:.0f} KRW am {f['kursdatum']}, {f['aktien_zahl'] / 1e6:.2f} Mio Aktien "
      f"({f['aktien_quelle']}): Marktkap. {mk_krw / 1e12:.1f} Bio KRW = {mk_krw / krw_je_usd / 1e9:.1f} Mrd USD bei {krw_je_usd:.0f}")
