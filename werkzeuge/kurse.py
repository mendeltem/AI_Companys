# -*- coding: utf-8 -*-
"""Kurse erneuern, ohne die Quartalszahlen anzufassen.

Die erzeugende Pipeline baut den ganzen Datenblock neu - Kurse, Quartale,
Segmente, Cashflows. Laeuft sie eine Woche nicht, veraltet die Seite als
Ganzes. Kurse aber sind taeglich zu haben, und sie sind die Haelfte jeder
Kennzahl auf dieser Seite: KGV, Kurs-Umsatz-Verhaeltnis und die Renditen
haengen alle am Zaehler.

Dieser Lauf erneuert deshalb genau das und nichts sonst:

    Kurse und Kursreihen, Wechselkurse, Kursdatum
    daraus neu: Marktkapitalisierung, KGV, KUV, Renditen ueber 1 und 3 Jahre

Nicht angefasst werden Quartale, Segmente und Cashflows. Deshalb bekommt der
Datenblock zwei Daten statt einem: stand fuer die Zahlen aus den Berichten,
stand_kurse fuer die Boersenkurse. Ein einzelnes Datum fuer beides waere eine
Behauptung, die nicht stimmt.

    python werkzeuge/kurse.py            # erneuern
    python werkzeuge/kurse.py --pruefen  # nur zeigen, was sich aendert
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402

TAKT = 1.2          # Sekunden zwischen zwei Abrufen; 0,4 war zu schnell, Yahoo drosselte
JAHRE = 3           # so weit reicht die Kursreihe der Seite


def _hole(symbol, bereich="3y", versuche=4):
    """Eine Kursreihe holen, mit Wiederholung.

    Yahoo drosselt nach einigen Dutzend Abrufen, und zwar nicht mit einem
    sauberen 429: Es kommen Zeitueberschreitungen, abgebrochene Verbindungen
    und sogar fehlschlagende Namensaufloesungen. Ohne Wiederholung fielen im
    ersten Lauf 22 von 66 Firmen aus - und zwar die ab dem 45. Abruf, also
    rein nach Alphabet, was den Fehler verraet. Deshalb hier wachsende Pausen
    statt eines einzigen Versuchs.
    """
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s"
           "?range=%s&interval=1d" % (urllib.parse.quote(symbol), bereich))
    anfrage = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
    })
    letzter = None
    for versuch in range(versuche):
        try:
            with urllib.request.urlopen(anfrage, timeout=30) as antwort:
                d = json.loads(antwort.read())
            break
        except Exception as f:
            letzter = f
            if versuch == versuche - 1:
                raise
            time.sleep(2 ** versuch * 2)   # 2, 4, 8 Sekunden
    erg = (d.get("chart") or {}).get("result") or []
    if not erg:
        raise RuntimeError("keine Kursreihe")
    r = erg[0]
    zeiten = r.get("timestamp") or []
    schluss = ((r.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    paare = [(datetime.fromtimestamp(t, timezone.utc).date().isoformat(), c)
             for t, c in zip(zeiten, schluss) if c is not None]
    if not paare:
        raise RuntimeError("Reihe leer")
    return [p[0] for p in paare], [round(p[1], 6) for p in paare]


def _fx(von):
    """Wechselkurs in Dollar, ueber das Paar XXXUSD=X."""
    if von == "USD":
        return 1.0
    _, schluss = _hole("%sUSD=X" % von, "5d")
    return schluss[-1]


def main():
    pruefen = "--pruefen" in sys.argv
    pfad = os.path.join(b.WURZEL, "nvidia-oekosystem.html")
    s = open(pfad, encoding="utf-8").read()
    m = re.search(r'(<script id="daten" type="application/json">)(.*?)(</script>)', s, re.S)
    D = json.loads(m.group(2))
    F, K = D["firmen"], D["kurse"]

    # Wechselkurse einmal je Waehrung, nicht je Firma.
    waehrungen = {e.get("waehrung") for e in F.values() if e.get("waehrung")}
    kurse_fx, fehler = {}, []
    for w in sorted(waehrungen):
        try:
            kurse_fx[w] = _fx(w)
            time.sleep(TAKT)
        except Exception as f:
            fehler.append(("FX " + w, str(f)[:70]))

    geaendert, unveraendert = [], 0
    for sym, e in sorted(F.items()):
        symbol = e.get("symbol")
        if not symbol:
            continue
        try:
            datum, schluss = _hole(symbol)
            time.sleep(TAKT)
        except Exception as f:
            fehler.append((sym, str(f)[:70]))
            continue
        alt_kurs, alt_datum = e.get("kurs"), e.get("kursdatum")
        neu_kurs, neu_datum = schluss[-1], datum[-1]
        if neu_datum == alt_datum and alt_kurs and abs(neu_kurs - alt_kurs) < 1e-9:
            unveraendert += 1
            continue

        # Kursreihe und Kurs.
        K[sym] = {"datum": datum, "close": schluss}
        e["kurs"], e["kursdatum"] = neu_kurs, neu_datum
        fx = kurse_fx.get(e.get("waehrung"), e.get("fx_usd") or 1.0)
        e["fx_usd"] = fx

        # Alles, was am Kurs haengt, neu rechnen. Was an den Quartalszahlen
        # haengt - Margen, Wachstum, Gewinn je Aktie - bleibt unberuehrt.
        n = e.get("aktien_zahl")
        if n:
            e["marktkap"] = neu_kurs * n
            e["marktkap_usd"] = e["marktkap"] * fx
            if e.get("umsatz_ttm"):
                e["kuv"] = e["marktkap"] / e["umsatz_ttm"]
            if e.get("op_q") and e["op_q"] > 0:
                e["kgv_q4x_op"] = e["marktkap"] / (e["op_q"] * 4)
        if e.get("eps_ttm"):
            e["kgv_ttm"] = neu_kurs / e["eps_ttm"] if e["eps_ttm"] > 0 else None
        if e.get("eps_q"):
            e["kgv_q4x"] = neu_kurs / (e["eps_q"] * 4) if e["eps_q"] > 0 else None
        if e.get("umsatz_ttm") and fx:
            e["umsatz_ttm_usd"] = e["umsatz_ttm"] * fx

        # Renditen aus der Reihe selbst, nicht aus einem gemerkten Wert.
        def rendite(tage):
            ziel = len(datum) - 1 - tage
            return ((neu_kurs / schluss[ziel] - 1) * 100) if 0 <= ziel < len(schluss) else None
        e["rendite_1j"] = rendite(252)
        e["rendite_3j"] = rendite(756)

        geaendert.append((sym, alt_kurs, neu_kurs, alt_datum, neu_datum))

    # Zwei Daten: eines fuer die Berichtszahlen, eines fuer die Kurse.
    stand_kurse = max((e.get("kursdatum") or "") for e in F.values())
    D["stand_kurse"] = stand_kurse

    print("%d Kurse erneuert, %d unveraendert, %d Fehler"
          % (len(geaendert), unveraendert, len(fehler)))
    print("Zahlen aus den Berichten: %s   Kurse: %s" % (D.get("stand"), stand_kurse))
    for sym, ak, nk, ad, nd in geaendert[:8]:
        print("   %-10s %s %s  ->  %s %s" % (sym, ad, ("%.2f" % ak) if ak else "-", nd, "%.2f" % nk))
    if len(geaendert) > 8:
        print("   ... und %d weitere" % (len(geaendert) - 8))
    for wo, was in fehler[:8]:
        print("   Fehler %-12s %s" % (wo, was))

    if pruefen:
        print("\n--pruefen: nichts geschrieben.")
        return 0
    if not geaendert:
        print("Nichts zu schreiben.")
        return 0
    neu = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(pfad, "w", encoding="utf-8", newline="").write(s[:m.start(2)] + neu + s[m.end(2):])
    print("\n-> %s" % pfad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
