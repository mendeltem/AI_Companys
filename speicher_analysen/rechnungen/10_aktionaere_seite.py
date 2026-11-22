# SK hynix: wem die Aktien gehoeren, alle zwei Monate ueber 36 Monate.
# Baut aus daten/skhynix_dart_aktionaere.csv (Tier 1a) und
# daten/skhynix_naver_handel.csv (Tier 2) die Datei aktionaere.json im
# Repository, die werkzeuge/aktionaere.py auf die Firmenseite setzt.
#
# Balkenhoehe = ausgegebene Aktien (sinkt bei Einzug, steigt bei Ausgabe).
# Segmente:
#   SK Square        DART, Aktienbuch / Bericht
#   NPS              DART, letzte Grossaktionaersmeldung (Stufe; Aenderungen
#                    unter 1 Punkt werden nicht gemeldet)
#   Auslaender       Naver/KRX-Anteil x gelistete Aktien (enthaelt ADR, Capital
#                    Group, BlackRock)
#   eigene Aktien    DART, letzter Bericht vor dem Stichtag
#   uebrige Inlaender Rest: Privatanleger und inlaendische Institutionen ohne NPS
#
# Gelistete Aktien bei KRX wechseln einige Tage nach dem rechtlichen Datum.
# Die Wechseltage stammen aus den Spruengen im Auslaenderanteil (Naver), die
# Stueckzahlen aus DART.

import csv
import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent
WURZEL = P.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}
kurs_usd = par["kurs_krw_usd"]

dart = list(csv.DictReader(open(P / "daten" / "skhynix_dart_aktionaere.csv", encoding="utf-8")))
handel = [z for z in csv.DictReader(open(P / "daten" / "skhynix_naver_handel.csv", encoding="utf-8"))
          if z["schluss_krw"]]

GELISTET = [("0000-00-00", 728002365), ("2026-02-23", 712702365), ("2026-07-29", 730492365), ("2026-11-17", 706799093)]
AUSGEGEBEN = [("0000-00-00", 728002365), ("2026-02-09", 712702365), ("2026-07-29", 730492365), ("2026-11-05", 706799093)]

def stufe(reihe, tag):
    wert = reihe[0][1]
    for ab, w in reihe:
        if ab <= tag:
            wert = w
    return wert

def aus_dart(posten, tag):
    z = sorted([(r["stichtag"], float(r["aktien"])) for r in dart if r["posten"] == posten])
    vorher = [w for d, w in z if d <= tag]
    return (vorher[-1] if vorher else z[0][1]), (not vorher)

# Stichtage: letzter Boersentag jedes zweiten Monats ab Nov 2023, dazu der juengste Tag
tage = [z["datum"] for z in handel]
monate = []
j, m = 2023, 11
while (j, m) <= (2026, 9):
    monate.append(f"{j}-{m:02d}")
    m += 2
    if m > 12:
        j, m = j + 1, m - 12
stichtage = [max(t for t in tage if t.startswith(mo)) for mo in monate] + [tage[-1]]
zeile = {z["datum"]: z for z in handel}

gruppen = {"sk_square": [], "nps": [], "auslaender": [], "inlaender": [], "eigene": []}
gesamt, kurs, angenaehert = [], [], []
for t in stichtage:
    z = zeile[t]
    n = stufe(AUSGEGEBEN, t)
    aus = float(z["auslaender_anteil_pct"]) / 100 * stufe(GELISTET, t)
    sk, f1 = aus_dart("sk_square", t)
    nps, f2 = aus_dart("nps", t)
    eig, f3 = aus_dart("eigene", t)
    rest = n - sk - nps - aus - eig
    for k, v in [("sk_square", sk), ("nps", nps), ("auslaender", aus), ("inlaender", rest), ("eigene", eig)]:
        gruppen[k].append(round(v / 1e6, 2))
    gesamt.append(round(n / 1e6, 2))
    kurs.append(round(float(z["schluss_krw"]) / kurs_usd, 1))
    if f1 or f3:
        angenaehert.append(t)

print("Stichtag   | gesamt | SK Sq |  NPS | Ausl. | Inl. | eigene | Kurs USD")
for i, t in enumerate(stichtage):
    print(f"{t} | {gesamt[i]:6.1f} | {gruppen['sk_square'][i]:5.1f} | {gruppen['nps'][i]:4.1f} | "
          f"{gruppen['auslaender'][i]:5.1f} | {gruppen['inlaender'][i]:5.1f} | {gruppen['eigene'][i]:5.1f} | {kurs[i]:7.1f}")
print("Fruehester DART-Stand vorgezogen fuer:", angenaehert)

# Nettokaeufe je Zwei-Monats-Fenster (Handel, nicht Bestand)
netto = {"netto_auslaender": [], "netto_institutionen": [], "netto_privat": []}
for i in range(1, len(stichtage)):
    fenster = [z for z in handel if stichtage[i - 1] < z["datum"] <= stichtage[i]]
    for k in netto:
        netto[k].append(round(sum(float(z[k] or 0) for z in fenster) / 1e6, 2))
print()
print("Fenster bis | Ausl. | Inst. | Privat (Mio Aktien netto)")
for i in range(1, len(stichtage)):
    print(f"{stichtage[i]} | {netto['netto_auslaender'][i - 1]:+6.1f} | {netto['netto_institutionen'][i - 1]:+6.1f} | {netto['netto_privat'][i - 1]:+6.1f}")

# Einstand: Durchschnittspreis der Nettokaeufe einer Gruppe in einem Zeitraum
def einstand(spalte, von, bis):
    f = [z for z in handel if von <= z["datum"] <= bis]
    menge = sum(float(z[spalte] or 0) for z in f)
    wert = sum(float(z[spalte] or 0) * float(z["schluss_krw"]) for z in f)
    return menge, (wert / menge / kurs_usd if menge else None)

print()
zeitraeume = [("2023-12-01", "2025-11-30"), ("2025-12-01", "2026-06-30"), ("2026-07-01", stichtage[-1]),
              ("2025-12-01", stichtage[-1])]
einstaende = {}
for spalte in ["netto_auslaender", "netto_institutionen", "netto_privat"]:
    for von, bis in zeitraeume:
        menge, preis = einstand(spalte, von, bis)
        einstaende[(spalte, von, bis)] = (menge, preis)
        p = f"{preis:7.1f} USD" if preis and menge > 0 else "  (netto Verkauf)"
        print(f"{spalte:20s} {von} bis {bis}: {menge / 1e6:+7.1f} Mio Aktien, Einstand {p}")

klein = sorted([(r["stichtag"], float(r["aktien"])) for r in dart if r["posten"] == "kleinaktionaere_anzahl"])
klein_akt = {r["stichtag"]: float(r["aktien"]) for r in dart if r["posten"] == "kleinaktionaere_aktien"}

# Kennzahlen fuer den Text
i_hoch = max(range(len(kurs)), key=lambda i: kurs[i])
hoch_tag = max(handel, key=lambda z: float(z["schluss_krw"]))
aus0, aus1 = gruppen["auslaender"][0], gruppen["auslaender"][-1]
aus_max_i = max(range(len(stichtage)), key=lambda i: gruppen["auslaender"][i])
pm, pp = einstaende[("netto_privat", "2025-12-01", "2026-06-30")]
am, ap = einstaende[("netto_auslaender", "2025-12-01", "2026-06-30")]
pm2, pp2 = einstaende[("netto_privat", "2025-12-01", stichtage[-1])]
jetzt = kurs[-1]

def nf(x, n=0):
    s = f"{x:,.{n}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

kopf_de = (f"{nf(gesamt[-1], 1)} Mio Aktien am {stichtage[-1]} · Kleinaktionäre {nf(klein[0][1])} (Dez 2023) → "
           f"{nf(klein[-1][1])} (Jun 2026) · Kurs {nf(kurs[0])} → {nf(float(hoch_tag['schluss_krw']) / kurs_usd)} "
           f"(Hoch {hoch_tag['datum']}) → {nf(jetzt)} USD")
kopf_en = (f"{gesamt[-1]:,.1f} m shares on {stichtage[-1]} · small shareholders {klein[0][1]:,.0f} (Dec 2023) → "
           f"{klein[-1][1]:,.0f} (Jun 2026) · price {kurs[0]:,.0f} → {float(hoch_tag['schluss_krw']) / kurs_usd:,.0f} "
           f"(high {hoch_tag['datum']}) → {jetzt:,.0f} USD")
these_de = (f"Die Zahl der Kleinaktionäre hat sich im ersten Halbjahr 2026 fast verdreifacht, auf "
            f"{nf(klein[-1][1] / 1e6, 2)} Mio. Gekauft haben vor allem Privatanleger: von Dez 2025 bis Jun 2026 netto "
            f"{nf(pm / 1e6, 1)} Mio Aktien zu durchschnittlich {nf(pp)} USD. Ausländer haben im selben Zeitraum netto "
            f"{nf(-am / 1e6, 1)} Mio Aktien abgegeben. Ihr Anteil sank von {nf(gruppen['auslaender'][aus_max_i] / gesamt[aus_max_i] * 100, 1)} % "
            f"({stichtage[aus_max_i][:7]}) auf {nf(aus1 / gesamt[-1] * 100, 1)} %, obwohl die ADR-Aktien hinzukamen. "
            f"Der Kurs liegt mit {nf(jetzt)} USD unter dem Einstand der Privatanleger seit Dez 2025 "
            f"({nf(pp2)} USD für netto {nf(pm2 / 1e6, 1)} Mio Aktien). Die Balken zeigen, wer hält, nicht, wie weit der Kurs fällt.")
these_en = (f"The number of small shareholders almost tripled in the first half of 2026, to {klein[-1][1] / 1e6:.2f} m. "
            f"Retail investors did most of the buying: Dec 2025 to Jun 2026 net {pm / 1e6:.1f} m shares at an average "
            f"{pp:,.0f} USD, while foreigners sold net {-am / 1e6:.1f} m. Their share fell from "
            f"{gruppen['auslaender'][aus_max_i] / gesamt[aus_max_i] * 100:.1f} % to {aus1 / gesamt[-1] * 100:.1f} %, despite the ADR shares. "
            f"At {jetzt:,.0f} USD the price is below retail's net entry since Dec 2025 ({pp2:,.0f} USD). "
            f"The bars show who holds, not how far the price can fall.")

daten = {
    "_stand": stichtage[-1],
    "SKHYNIX": {
        "stichtage": stichtage,
        "gesamt": gesamt,
        "kurs_usd": kurs,
        "gruppen": [
            {"name": {"de": "SK Square", "en": "SK Square"}, "farbe": "#2C6E9E", "werte": gruppen["sk_square"]},
            {"name": {"de": "NPS (Rentenkasse)", "en": "NPS (pension fund)"}, "farbe": "#4C8A8A", "werte": gruppen["nps"]},
            {"name": {"de": "Ausländer (inkl. ADR)", "en": "Foreign (incl. ADR)"}, "farbe": "var(--akzent)", "werte": gruppen["auslaender"]},
            {"name": {"de": "Übrige Inländer (Privat, Institutionen)", "en": "Other domestic (retail, institutions)"}, "farbe": "#B07414", "werte": gruppen["inlaender"]},
            {"name": {"de": "Eigene Aktien", "en": "Treasury shares"}, "farbe": "var(--neutral)", "werte": gruppen["eigene"]},
        ],
        "netto": [
            {"name": {"de": "Ausländer", "en": "Foreign"}, "farbe": "var(--akzent)", "werte": netto["netto_auslaender"]},
            {"name": {"de": "Institutionen (inkl. NPS)", "en": "Institutions (incl. NPS)"}, "farbe": "#5B3FA8", "werte": netto["netto_institutionen"]},
            {"name": {"de": "Privatanleger", "en": "Retail"}, "farbe": "#B07414", "werte": netto["netto_privat"]},
        ],
        "kleinaktionaere": [{"stichtag": d, "anzahl": int(a), "aktien_mio": round(klein_akt[d] / 1e6, 1)} for d, a in klein],
        "kopf": {"de": kopf_de, "en": kopf_en},
        "these": {"de": these_de, "en": these_en},
        "hinweis": {
            "de": ("Balkenhöhe: ausgegebene Aktien (DART). SK Square, eigene Aktien: letzter Bericht vor dem Stichtag (DART, Tier 1a). "
                   "NPS: letzte Großaktionärsmeldung, Änderungen unter 1 Punkt werden nicht gemeldet. Ausländer: KRX-Anteil über Naver (Tier 2) "
                   "mal gelistete Aktien, mit den ADR-Aktien. Übrige Inländer: Rest. Nettokäufe: Börsenhandel je Gruppe, ohne Umtausch und Ausgabe. "
                   "Kurs in USD zu festen 1.350 KRW. Einstand: Nettokauf mal Schlusskurs, grob."),
            "en": ("Bar height: shares issued (DART). SK Square, treasury: latest report before the date (DART, tier 1a). NPS: latest "
                   "5 % filing, changes below 1 point are not filed. Foreign: KRX share via Naver (tier 2) times listed shares, incl. ADR. "
                   "Other domestic: remainder. Net purchases: exchange trading by group. Price in USD at a fixed 1,350 KRW."),
        },
    },
}
ziel = WURZEL / "aktionaere.json"
json.dump(daten, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print()
print(kopf_de)
print(these_de)
print("geschrieben:", ziel)
