# -*- coding: utf-8 -*-
"""Stellt je Firma zusammen, was fuer eine Beurteilung noetig ist.

Kein Modell, nur Arithmetik und Auswahl: Zahlenreihe, rechnerisch gefundene
Auffaelligkeiten, Bewertung, Ertragslage. Das Urteil kommt danach und
anderswoher - hier wird nur sichergestellt, dass es auf etwas Nachpruefbarem
fusst und nicht auf einem Gefuehl.

    python werkzeuge/beleglage.py            # alle, kompakt auf die Konsole
    python werkzeuge/beleglage.py NVDA       # eine Firma, ausfuehrlich
    python werkzeuge/beleglage.py --json     # als Datei fuer die Weiterarbeit
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402


def _fx(e):
    """Faktor in Dollar. Die Rohdaten stehen in der Heimatwaehrung."""
    return e.get("fx_usd") or 1.0


def _reihe(e, feld, n=8):
    q = sorted(e.get("quartale", []), key=lambda z: z["ende"], reverse=True)[:n]
    return [(z["ende"], z.get(feld)) for z in q]


def _yoy(e, feld="umsatz"):
    q = sorted(e.get("quartale", []), key=lambda z: z["ende"], reverse=True)
    raus = []
    for i in range(min(4, max(0, len(q) - 4))):
        jetzt, vor = q[i].get(feld), q[i + 4].get(feld)
        raus.append((q[i]["ende"], (jetzt / vor - 1) * 100 if jetzt and vor and vor > 0 else None))
    return raus


def _auffaellig(e):
    """Was rechnerisch aus der Reihe faellt. Ohne Deutung."""
    raus = []
    w = _yoy(e)
    if len(w) >= 2 and w[0][1] is not None and w[1][1] is not None:
        d = w[0][1] - w[1][1]
        if abs(d) >= 10:
            raus.append("Umsatzwachstum %+.0f%% nach %+.0f%% (%+.0f Punkte)" % (w[0][1], w[1][1], d))
    q = sorted(e.get("quartale", []), key=lambda z: z["ende"], reverse=True)
    if q:
        j = q[0]
        if j.get("operativmarge") is not None and len(q) > 4 and q[4].get("operativmarge") is not None:
            d = j["operativmarge"] - q[4]["operativmarge"]
            if abs(d) >= 5:
                raus.append("operative Marge %+.1f Punkte auf %.1f%% zum Vorjahresquartal"
                            % (d, j["operativmarge"]))
        if j.get("netto") is not None and j.get("operativ"):
            ab = (j["netto"] - j["operativ"]) / abs(j["operativ"]) * 100
            if abs(ab) >= 25:
                raus.append("Nettoergebnis %+.0f%% neben dem operativen - betriebsfremde Posten"
                            % ab)
        if j.get("umsatz") and j.get("operativ") is not None and j["operativ"] < 0:
            raus.append("operativ im Verlust")
    return raus


def lage(sym, e, wert):
    fx = _fx(e)
    kurs = e.get("kurs")
    eps_q, eps_ttm = e.get("eps_q"), e.get("eps_ttm")
    q = sorted(e.get("quartale", []), key=lambda z: z["ende"], reverse=True)
    op_q = q[0].get("operativ") if q else None
    aktien = e.get("aktien_zahl")
    op_je = (op_q / aktien) if (op_q is not None and aktien) else None
    w = wert.get(sym, {})
    return {
        "ticker": sym,
        "name": e.get("name"),
        "rolle": e.get("rolle"),
        "waehrung": e.get("waehrung"),
        "marktkap_usd": e.get("marktkap_usd"),
        "kurs_usd": kurs * fx if kurs else None,
        "umsatz_ttm_usd": e.get("umsatz_ttm_usd"),
        "umsatz_yoy": e.get("umsatz_yoy"),
        "umsatz_yoy_reihe": [(d, None if v is None else round(v, 1)) for d, v in _yoy(e)],
        "bruttomarge": e.get("bruttomarge"),
        "operativmarge": e.get("operativmarge"),
        "kgv_ttm": e.get("kgv_ttm"),
        "kgv_q4x": e.get("kgv_q4x"),
        "kgv_q4x_op": e.get("kgv_q4x_op"),
        "rendite_q": (eps_q * 4 / kurs * 100) if (eps_q and kurs) else None,
        "rendite_ttm": (eps_ttm / kurs * 100) if (eps_ttm and kurs) else None,
        "rendite_op_q": (op_je * 4 / kurs * 100) if (op_je and kurs) else None,
        "innerer_wert": w.get("wert"),
        "wert_grund": None if w.get("wert") else w.get("grund"),
        "wert_basis": w.get("basis_art"),
        "wert_endwertanteil": w.get("endwertanteil"),
        "fcf": w.get("fcf"),
        "kurs_1j": e.get("rendite_1j"),
        "kurs_3j": e.get("rendite_3j"),
        "n_quartale": e.get("n_quartale"),
        "auffaellig": _auffaellig(e),
        "umsatz_reihe_usd": [(d, None if v is None else round(v * fx / 1e9, 2))
                             for d, v in _reihe(e, "umsatz", 6)],
        "operativ_reihe_usd": [(d, None if v is None else round(v * fx / 1e9, 2))
                               for d, v in _reihe(e, "operativ", 6)],
    }


def main():
    D, _ = b.daten_der_seite()
    F = D["firmen"]
    p = b._pfad("wert.json")
    wert = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    alle = {s: lage(s, F[s], wert) for s in (args or F) if s in F}

    if "--json" in sys.argv:
        ziel = b._pfad("beleglage.json")
        json.dump(alle, open(ziel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%d Firmen -> %s" % (len(alle), ziel))
        return

    for s, l in alle.items():
        z = lambda v, n=1: "—" if v is None else ("%.*f" % (n, v))
        print("%-10s %-28s Mk %7s Mrd  Umsatz %6s Mrd  YoY %6s%%  opM %5s%%  "
              "KGVq %6s  RendQ %5s%%  Wert %8s  %s"
              % (s, (l["name"] or "")[:28],
                 z((l["marktkap_usd"] or 0) / 1e9, 0), z((l["umsatz_ttm_usd"] or 0) / 1e9, 1),
                 z(l["umsatz_yoy"], 0), z(l["operativmarge"], 0), z(l["kgv_q4x"], 1),
                 z(l["rendite_q"], 1), z(l["innerer_wert"], 2),
                 "; ".join(l["auffaellig"])[:60]))


if __name__ == "__main__":
    main()
