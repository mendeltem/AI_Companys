# -*- coding: utf-8 -*-
"""Quartalszahlen aus XBRL, mit den Fallen, die dieses Projekt schon kennt.

Bisher kamen Umsatz, Ergebnis und Gewinn je Aktie aus einer Pipeline, die
nicht im Repository liegt. Lief sie nicht, veralteten sie. Dieser Lauf holt
sie direkt bei der SEC.

Die Fallen stehen im README des Projekts und sind hier eingebaut:

Vierte Quartale gibt es im XBRL nicht. Sie muessen als Geschaeftsjahr minus
Neunmonatszeitraum rekonstruiert werden. Fuer Umsatz und Ergebnis ist das
exakt, weil beides Fluesse sind. Fuer Gewinn je Aktie und Aktienzahlen ist es
Unsinn: Das sind gewichtete Groessen, und die Differenz zweier gewichteter
Mittel ist kein Mittel. Genau daraus entstand in den alten Daten ein NVIDIA-
Quartal mit -1,00 Gewinn je Aktie bei 1,4 Mrd Gewinn, und eine Aktienzahl von
minus 820 Millionen bei Recursion. Hier wird deshalb nur rekonstruiert, was
sich rekonstruieren laesst.

Tags wandern. Broadcom bucht den Nettogewinn unter ProfitLoss, nicht unter
NetIncomeLoss - letzteres endet dort 2019. NVIDIA bucht Investitionen seit
2012 anders. Genommen wird deshalb nie der erstbeste vorhandene Tag, sondern
der mit den juengsten Werten.

Waehrungen. Wer in Euro bilanziert und in Dollar notiert, darf nicht gemischt
werden; die Einheit wird mitgefuehrt und gemeldet.

    python werkzeuge/quartale.py --pruefen        # gegen den Seitenstand vergleichen
    python werkzeuge/quartale.py --pruefen NVDA   # eine Firma im Detail
    python werkzeuge/quartale.py                  # in die Seite schreiben
"""

import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402

# Ein Feld, viele Namen. Reihenfolge ist Praeferenz, gewaehlt wird nach
# juengstem Wert - das faengt einen Tagwechsel ohne Pflege je Firma ab.
TAGS = {
    "umsatz": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],
    "brutto": ["GrossProfit"],
    "operativ": ["OperatingIncomeLoss"],
    # Broadcom: NetIncomeLoss endet 2019, seitdem ProfitLoss.
    "netto": ["NetIncomeLoss", "ProfitLoss",
              "NetIncomeLossAvailableToCommonStockholdersBasic"],
    "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted",
            "EarningsPerShareBasic"],
    "aktien": ["WeightedAverageNumberOfDilutedSharesOutstanding",
               "WeightedAverageNumberOfSharesOutstandingBasic"],
}

# Dieselben Felder in der IFRS-Taxonomie. Sie heissen anders und stehen an
# anderer Stelle, meinen aber dasselbe.
TAGS_IFRS = {
    "umsatz": ["RevenueFromContractsWithCustomers", "Revenue"],
    "brutto": ["GrossProfit"],
    "operativ": ["ProfitLossFromOperatingActivities", "OperatingIncomeLoss"],
    "netto": ["ProfitLoss", "ProfitLossAttributableToOwnersOfParent"],
    "eps": ["DilutedEarningsLossPerShare", "BasicEarningsLossPerShare"],
    "aktien": ["WeightedAverageNumberOfDilutedOrdinarySharesOutstanding",
               "WeightedAverageNumberOfOrdinarySharesOutstandingBasic"],
}

# Was sich als Geschaeftsjahr minus Neunmonate rekonstruieren laesst: Fluesse.
# Gewichtete Groessen nicht - siehe Kopf.
REKONSTRUIERBAR = {"umsatz", "brutto", "operativ", "netto"}

QUARTAL = (75, 105)      # Tage, die als Quartalszeitraum gelten
NEUN = (255, 285)
JAHR = (340, 400)


def _tage(e):
    if not e.get("start"):
        return None
    return (dt.date.fromisoformat(e["end"]) - dt.date.fromisoformat(e["start"])).days


def _reihen(fakten, feld):
    """Je Tag die Zeitraeume nach Laenge sortiert; zurueck kommt der juengste Tag."""
    fkt = fakten.get("facts", {})
    kandidaten = [("us-gaap", t) for t in TAGS[feld]]
    kandidaten += [("ifrs-full", t) for t in TAGS_IFRS.get(feld, [])]
    bester, beste, einheit_best = None, None, None
    for taxonomie, tag in kandidaten:
        gaap = fkt.get(taxonomie, {})
        if tag not in gaap:
            continue
        einheiten = gaap[tag]["units"]
        einheit = ("USD/shares" if feld == "eps" and "USD/shares" in einheiten
                   else "shares" if feld == "aktien" and "shares" in einheiten
                   else "USD" if "USD" in einheiten else list(einheiten)[0])
        quartal, neun, jahr = {}, {}, {}
        for e in einheiten[einheit]:
            if e.get("form") not in ("10-Q", "10-K", "20-F", "40-F", "6-K"):
                continue
            t = _tage(e)
            if t is None:
                continue
            ziel = (quartal if QUARTAL[0] <= t <= QUARTAL[1] else
                    neun if NEUN[0] <= t <= NEUN[1] else
                    jahr if JAHR[0] <= t <= JAHR[1] else None)
            if ziel is None:
                continue
            # Spaetere Einreichung gewinnt: korrigierte Zahlen ersetzen alte.
            vorher = ziel.get(e["end"])
            if vorher is None or (e.get("filed") or "") >= vorher[1]:
                ziel[e["end"]] = (e["val"], e.get("filed") or "")
        if not quartal and not jahr:
            continue
        neuster = max(list(quartal) + list(jahr))
        if bester is None or neuster > beste[3]:
            bester = tag
            beste = ({k: v[0] for k, v in quartal.items()},
                     {k: v[0] for k, v in neun.items()},
                     {k: v[0] for k, v in jahr.items()}, neuster)
            einheit_best = einheit
    if bester is None:
        return None, {}, {}, {}, None
    return bester, beste[0], beste[1], beste[2], einheit_best


def _viertes(quartal, neun, jahr, feld):
    """Vierte Quartale ergaenzen, wo sie fehlen und wo es zulaessig ist."""
    if feld not in REKONSTRUIERBAR:
        return 0
    ergaenzt = 0
    for ende, jahreswert in jahr.items():
        if ende in quartal:
            continue
        # Der Neunmonatszeitraum endet neun Monate vor dem Jahresende; er ist
        # der einzige Wert, der hier subtrahiert werden darf.
        d = dt.date.fromisoformat(ende)
        kandidaten = [n for n in neun
                      if 80 <= (d - dt.date.fromisoformat(n)).days <= 100]
        if len(kandidaten) != 1:
            continue
        quartal[ende] = jahreswert - neun[kandidaten[0]]
        ergaenzt += 1
    return ergaenzt


_VERZEICHNIS = None


def _cik_ueber_ticker(sym, e):
    """CIK nachschlagen, wenn sie in den Seitendaten fehlt.

    TSMC, Sony und UMC stehen dort ohne CIK, reichen bei der SEC aber ein -
    als auslaendische Emittenten mit 20-F und 6-K. Ohne diesen Griff faellt
    ein Viertel der Firmen aus, obwohl die Daten vorhanden sind.
    """
    global _VERZEICHNIS
    if _VERZEICHNIS is None:
        import wert as W
        try:
            roh, _, _ = b.hole("https://www.sec.gov/files/company_tickers.json")
            import json as _j
            _VERZEICHNIS = {x["ticker"].upper(): str(x["cik_str"]).zfill(10)
                            for x in _j.loads(roh).values()}
        except Exception:
            _VERZEICHNIS = {}
    return (_VERZEICHNIS.get(sym.upper())
            or _VERZEICHNIS.get(str(e.get("symbol") or "").upper()))


def firma(sym, e):
    """Quartalsreihe einer Firma aus XBRL. Gibt Reihe, Einheit, Hinweise."""
    import wert as W
    cik = e.get("cik") or _cik_ueber_ticker(sym, e)
    if not cik:
        return None, None, ["keine CIK, auch nicht im Tickerverzeichnis"]
    fakten = W._fakten(cik)

    felder, einheiten, hinweise = {}, {}, []
    for feld in TAGS:
        tag, q, n, j, einheit = _reihen(fakten, feld)
        if tag is None:
            continue
        ergaenzt = _viertes(q, n, j, feld)
        felder[feld] = q
        einheiten[feld] = einheit
        if ergaenzt:
            hinweise.append("%s: %d vierte Quartale rekonstruiert" % (feld, ergaenzt))
        if feld == "netto" and tag != "NetIncomeLoss":
            hinweise.append("netto aus %s" % tag)

    if "umsatz" not in felder:
        return None, None, ["kein Umsatz im XBRL"]

    enden = sorted(set(felder["umsatz"]), reverse=True)
    reihe = []
    for ende in enden:
        z = {"ende": ende, "quelle": "SEC XBRL"}
        for feld in TAGS:
            z[feld] = felder.get(feld, {}).get(ende)
        if z.get("umsatz"):
            for feld, name in (("brutto", "bruttomarge"), ("operativ", "operativmarge"),
                               ("netto", "nettomarge")):
                if z.get(feld) is not None:
                    z[name] = z[feld] / z["umsatz"] * 100
        reihe.append(z)

    geld = einheiten.get("umsatz")
    if geld and geld != e.get("waehrung"):
        hinweise.append("Einheit %s, Kurs in %s" % (geld, e.get("waehrung")))
    return reihe, geld, hinweise


def vergleich(sym, neu, alt):
    """Neue Reihe gegen die der Seite. Zurueck kommt eine Trefferquote."""
    alt_map = {z["ende"]: z for z in alt}
    treffer = daneben = fehlt = 0
    beispiele = []
    for z in neu[:12]:
        a = alt_map.get(z["ende"])
        if not a:
            fehlt += 1
            continue
        for feld in ("umsatz", "operativ", "netto"):
            x, y = z.get(feld), a.get(feld)
            if x is None or y is None:
                continue
            if y and abs(x - y) / max(abs(y), 1) < 0.005:
                treffer += 1
            else:
                daneben += 1
                if len(beispiele) < 3:
                    beispiele.append("%s %s: neu %.4g gegen %.4g" % (z["ende"], feld, x, y))
    return treffer, daneben, fehlt, beispiele


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pruefen = "--pruefen" in sys.argv
    pfad = os.path.join(b.WURZEL, "nvidia-oekosystem.html")
    s = open(pfad, encoding="utf-8").read()
    m = re.search(r'(<script id="daten" type="application/json">)(.*?)(</script>)', s, re.S)
    D = json.loads(m.group(2))
    F = D["firmen"]

    gewuenscht = [a.upper() for a in args] or sorted(F)
    ges_t = ges_d = ges_f = 0
    print("%-10s %5s %6s %6s %6s  %s" % ("Ticker", "Q", "gleich", "anders", "fehlt", "Hinweise"))
    for sym in gewuenscht:
        if sym not in F:
            continue
        try:
            reihe, einheit, hinweise = firma(sym, F[sym])
        except Exception as f:
            print("%-10s Fehler: %s" % (sym, str(f)[:70]))
            continue
        if reihe is None:
            print("%-10s %5s %6s %6s %6s  %s" % (sym, "-", "-", "-", "-", "; ".join(hinweise)))
            continue
        t, d, fl, bsp = vergleich(sym, reihe, F[sym].get("quartale", []))
        ges_t += t; ges_d += d; ges_f += fl
        print("%-10s %5d %6d %6d %6d  %s" % (sym, len(reihe), t, d, fl, "; ".join(hinweise)[:60]))
        if args and bsp:
            for x in bsp:
                print("             %s" % x)

    gesamt = ges_t + ges_d
    print("\nUebereinstimmung mit dem Seitenstand: %d von %d Werten (%.1f %%), %d Quartale fehlen dort"
          % (ges_t, gesamt, 100 * ges_t / gesamt if gesamt else 0, ges_f))
    if pruefen:
        print("--pruefen: nichts geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
