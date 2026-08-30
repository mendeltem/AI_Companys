# -*- coding: utf-8 -*-
"""Innerer Wert je Firma aus den Zahlen der Einreichungen, ohne Blick auf den Kurs.

Gerechnet wird ein abgezinster Zahlungsstrom: was die Firma an freiem Geld
abwirft, zehn Jahre fortgeschrieben, danach ein Endwert, alles auf heute
abgezinst, Nettoschulden abgezogen, durch die Aktienzahl geteilt.

    freier Cashflow   = operativer Cashflow - Investitionen
    Unternehmenswert  = Summe FCF_j / (1+r)^j  +  Endwert / (1+r)^n
    Endwert           = FCF_n * (1+g) / (r - g)
    Eigenkapitalwert  = Unternehmenswert - Nettoschulden
    innerer Wert      = Eigenkapitalwert / Aktien

Zwei Dinge, die man wissen muss, bevor man die Zahl benutzt:

Der Abzinssatz r ist gesetzt, nicht gemessen. Im Lehrbuch kaeme er aus dem
CAPM, dessen Beta aus der Kursreihe geschaetzt wird - dann haenge der
angeblich kursunabhaengige Wert doch wieder am Kurs. Hier steht deshalb eine
feste Huerde. Das ist eine Konvention, und sie gehoert neben die Zahl.

Der Endwert traegt bei Wachstumsfirmen 70 bis 85 Prozent des Ergebnisses. Die
Zahl ist damit ueberwiegend eine Aussage ueber Jahr elf und danach, nicht ueber
das laufende Geschaeft. Wer sie auf zwei Stellen liest, liest zu genau.

Aufruf:
    python werkzeuge/wert.py            # alle Firmen mit CIK
    python werkzeuge/wert.py NVDA MU    # nur diese
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402

# Feste Annahmen. Sichtbar hier oben, damit sie mit der Zahl mitwandern.
ABZINSUNG = 0.10          # Huerde, die eine Investition nehmen muss
ENDWACHSTUM = 0.03        # ewiges Wachstum ab Jahr elf, knapp Weltwirtschaft
JAHRE = 10                # Fortschreibung vor dem Endwert
WACHSTUM_DECKEL = 0.20    # kein Unternehmen waechst zehn Jahre schneller
WACHSTUM_BODEN = -0.05

# Ein Feld, viele Namen. Die Reihenfolge ist die Praeferenz; genommen wird der
# Tag mit den juengsten Werten, nicht der erste, der existiert. NVIDIA etwa
# bucht Investitionen seit 2012 nicht mehr unter dem ueblichen Tag - wer den
# nimmt, rechnet den freien Cashflow um Milliarden zu hoch.
TAGS = {
    "cashflow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "investitionen": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        "PaymentsForCapitalImprovements",
        "PaymentsToAcquireOtherPropertyPlantAndEquipment",
    ],
    "geld": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "anlagen": [
        "ShortTermInvestments",
        "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
        "MarketableSecuritiesCurrent",
    ],
    "schulden_lang": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "schulden_kurz": ["LongTermDebtCurrent", "ShortTermBorrowings", "CommercialPaper"],
    "aktien": [
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
    ],
}


def _fakten(cik):
    roh, _, _ = b.hole("https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % str(cik).zfill(10))
    return json.loads(roh)


def _jahreswerte(fakten, tags, fluss=True):
    """Jahreswerte eines Feldes, samt dem Tag, aus dem sie stammen.

    Fluesse (Cashflow, Investitionen) kommen aus Zeitraeumen von rund einem
    Jahr; Bestaende (Geld, Schulden, Aktien) sind Stichtagswerte. Gewaehlt wird
    unter den vorhandenen Tags derjenige mit dem juengsten Wert - genau das
    faengt einen Tagwechsel ab, ohne dass man ihn je Firma von Hand pflegt.
    """
    gaap = fakten.get("facts", {}).get("us-gaap", {})
    bester, beste_reihe, beste_einheit = None, {}, None
    for tag in tags:
        if tag not in gaap:
            continue
        einheiten = gaap[tag]["units"]
        einheit = "USD" if "USD" in einheiten else list(einheiten)[0]
        reihe = {}
        for e in einheiten[einheit]:
            if e.get("form") not in ("10-K", "10-K/A", "20-F", "40-F"):
                continue
            if fluss:
                if not e.get("start"):
                    continue
                import datetime as dt
                tage = (dt.date.fromisoformat(e["end"]) - dt.date.fromisoformat(e["start"])).days
                if not 340 <= tage <= 400:
                    continue
            elif e.get("start"):
                continue
            reihe[e["end"][:4]] = e["val"]
        if not reihe:
            continue
        if bester is None or max(reihe) > max(beste_reihe):
            bester, beste_reihe, beste_einheit = tag, reihe, einheit
    return bester, beste_reihe, beste_einheit


def _basis_und_wachstum(fcf):
    """Ausgangswert und Wachstumsrate in einem Schritt, aus derselben Geraden.

    Die eigentliche Schwierigkeit ist, eine Rampe von einem Zyklus zu
    unterscheiden. NVIDIAs Reihe 8 - 4 - 27 - 61 - 97 schwankt heftig und ist
    trotzdem kein Zyklus; Microns 2,4 - 3,1 - (-6,1) - 0,1 - 1,7 schwankt
    aehnlich stark und ist einer. Ein Streuungsmass sieht beide gleich.

    Die Bestimmtheit der logarithmischen Ausgleichsgeraden sieht den Unterschied:
    Bei der Rampe liegen die Punkte nahe an der Geraden, bei der Zykluskurve
    nicht. Sitzt die Gerade gut, ist ihr Wert im letzten Jahr die Basis - das
    glaettet ein einzelnes Ausreisserjahr, ohne den Trend wegzumitteln. Sitzt
    sie schlecht, gibt es keinen Trend, den man fortschreiben duerfte, und die
    Basis ist der Mittelwert ueber den ganzen Zeitraum.

    Rueckgabe: (Basis, Wachstum, Art, Bestimmtheit)
    """
    import math
    jahre = sorted(fcf)
    werte = [fcf[j] for j in jahre]
    punkte = [(int(j), fcf[j]) for j in jahre if fcf[j] > 0]
    if len(punkte) >= 3:
        xs = [p[0] for p in punkte]
        ys = [math.log(p[1]) for p in punkte]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        unten = sum((x - mx) ** 2 for x in xs)
        if unten:
            steigung = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / unten
            achse = my - steigung * mx
            rest = sum((y - (achse + steigung * x)) ** 2 for x, y in zip(xs, ys))
            gesamt = sum((y - my) ** 2 for y in ys)
            r2 = 1 - rest / gesamt if gesamt else 0.0
            # Fehlende Jahre zaehlen gegen den Trend: wer zwischendurch negativ
            # war, hat keine Rampe, auch wenn die uebrigen Punkte gut liegen.
            if r2 >= 0.7 and len(punkte) == len(jahre):
                basis = math.exp(achse + steigung * int(jahre[-1]))
                w = max(WACHSTUM_BODEN, min(WACHSTUM_DECKEL, math.exp(steigung) - 1))
                return basis, w, "Trend", r2
            return sum(werte) / len(werte), None, "Mittel", r2
    return sum(werte) / len(werte), None, "Mittel", 0.0


def _umsatzwachstum(quartale):
    """Jahreswachstum aus der Umsatzreihe, als Ersatz fuer die Fortschreibung.

    Wenn der freie Cashflow keinen Trend hergibt, heisst das nicht, dass die
    Firma nicht waechst - Investitionszyklen und Working Capital schlagen dort
    durch, im Umsatz nicht. Eli Lilly kaeme sonst auf drei Prozent, bei einem
    Cashflow, der sich gerade verdoppelt hat. Der Umsatz ist die glattere Reihe
    und die ehrlichere Grundlage; unterstellt wird dabei, dass die Marge auf
    dem freien Cashflow bleibt, wo sie ist.
    """
    import math
    punkte = []
    for q in quartale:
        u = q.get("umsatz")
        if u and u > 0:
            jahr = int(q["ende"][:4]) + (int(q["ende"][5:7]) - 1) / 12.0
            punkte.append((jahr, math.log(u)))
    if len(punkte) < 6:
        return None
    xs = [p[0] for p in punkte]
    ys = [p[1] for p in punkte]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    unten = sum((x - mx) ** 2 for x in xs)
    if not unten:
        return None
    steigung = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / unten
    return max(WACHSTUM_BODEN, min(WACHSTUM_DECKEL, math.exp(steigung) - 1))


def _wachstum(reihe):
    """Jaehrliches Wachstum als Ausgleichsgerade durch die logarithmierte Reihe.

    Nicht Endpunkt gegen Endpunkt: Apple kaeme so auf 1,5 Prozent, weil Anfangs-
    und Endjahr zufaellig gleich hoch liegen, obwohl das Jahr dazwischen deutlich
    darueber lag. Die Gerade nimmt alle Jahre mit und ist gegen einen einzelnen
    Ausreisser unempfindlich. Negative Jahre koennen nicht logarithmiert werden
    und fallen heraus; bleiben weniger als drei uebrig, gibt es keine Rate.
    """
    import math
    punkte = [(int(j), reihe[j]) for j in sorted(reihe) if reihe[j] > 0]
    if len(punkte) < 3:
        return None
    xs = [p[0] for p in punkte]
    ys = [math.log(p[1]) for p in punkte]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    unten = sum((x - mx) ** 2 for x in xs)
    if not unten:
        return None
    steigung = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / unten
    return max(WACHSTUM_BODEN, min(WACHSTUM_DECKEL, math.exp(steigung) - 1))


def _basis(fcf):
    """Der Ausgangswert der Fortschreibung, bei Zyklikern geglaettet.

    Das letzte Jahr als Basis zu nehmen ist bei stetigen Geschaeften richtig und
    bei zyklischen falsch: Micron traefe damit je nach Zeitpunkt ein Tal oder
    einen Gipfel und bekaeme einen Wert, der ueber Jahre um das Mehrfache
    schwankt, ohne dass sich die Firma geaendert haette. Schwankt die Reihe
    stark - Streuung ueber der Haelfte des Mittelwerts -, wird deshalb ueber
    drei Jahre gemittelt und das vermerkt.
    """
    jahre = sorted(fcf)
    werte = [fcf[j] for j in jahre]
    mittel = sum(werte) / len(werte)
    if mittel <= 0:
        return fcf[jahre[-1]], False
    streuung = (sum((v - mittel) ** 2 for v in werte) / len(werte)) ** 0.5
    if streuung / abs(mittel) > 0.5:
        return mittel, True
    return fcf[jahre[-1]], False


def innerer_wert(sym, e):
    """Rechnet eine Firma durch. Gibt ein Ergebnis oder einen Grund zurueck."""
    cik = e.get("cik")
    if not cik:
        return {"ticker": sym, "wert": None, "grund": "keine SEC-Einreichungen, kein XBRL"}
    try:
        f = _fakten(cik)
    except Exception as fehler:
        return {"ticker": sym, "wert": None, "grund": "XBRL nicht abrufbar: %s" % str(fehler)[:80]}

    tag_cf, cf, einheit = _jahreswerte(f, TAGS["cashflow"])
    tag_inv, inv, _ = _jahreswerte(f, TAGS["investitionen"])
    if not cf:
        return {"ticker": sym, "wert": None, "grund": "kein operativer Cashflow im XBRL"}

    # Waehrungsfalle, dieselbe wie beim KGV: ASML reicht bei der SEC ein, rechnet
    # darin aber in Euro, waehrend der Kurs auf dieser Seite in Dollar steht. Ein
    # innerer Wert in Euro neben einem Dollarkurs sieht aus wie ein Vergleich und
    # ist keiner. Ohne belastbaren Umrechnungskurs gibt es deshalb keine Zahl.
    kurswaehrung = e.get("waehrung")
    if einheit and kurswaehrung and einheit != kurswaehrung:
        return {"ticker": sym, "wert": None, "einheit": einheit,
                "tag_cashflow": tag_cf, "tag_investitionen": tag_inv,
                "grund": "Zahlen stehen in %s, der Kurs in %s - ohne Umrechnungskurs ist "
                         "der Vergleich keiner" % (einheit, kurswaehrung)}

    jahre = sorted(set(cf) & set(inv)) if inv else sorted(cf)
    if len(jahre) < 2:
        return {"ticker": sym, "wert": None, "grund": "zu wenige Jahre (%d)" % len(jahre)}
    jahre = jahre[-5:]
    fcf = {j: cf[j] - inv.get(j, 0) for j in jahre}

    letzter, w, art, r2 = _basis_und_wachstum(fcf)
    if w is None:
        w = _umsatzwachstum(e.get("quartale") or [])
        art = "Mittel/Umsatz" if w is not None else "Mittel/pauschal"
        if w is None:
            w = ENDWACHSTUM
    if letzter <= 0:
        grund = ("freier Cashflow ueber den Zeitraum %s bis %s im Mittel nicht positiv "
                 "(%.3g) - was hereinkommt, geht in den Ausbau; ein abgezinster "
                 "Zahlungsstrom ergibt hier keine Aussage" % (jahre[0], jahre[-1], letzter))
        return {"ticker": sym, "wert": None, "waehrung": e.get("waehrung_heim") or e.get("waehrung"),
                "fcf": fcf, "basis_art": art, "bestimmtheit": r2,
                "tag_cashflow": tag_cf, "tag_investitionen": tag_inv, "grund": grund}

    # Bleibt ueber den ganzen Zeitraum kaum freies Geld uebrig, ist die Zahl am
    # Ende zwar rechenbar, aber keine Aussage: Sie haengt dann fast ganz an
    # einem Basisjahr, das ebensogut anders haette ausfallen koennen. Micron ist
    # der Fall - was operativ hereinkommt, geht seit Jahren in neue Fabriken.
    # Eine winzige Zahl neben einem dreistelligen Kurs behauptet mehr, als die
    # Rechnung traegt; deshalb hier ein Strich mit Begruendung.
    umsatz = e.get("umsatz_ttm")
    if umsatz and letzter / umsatz < 0.03:
        return {"ticker": sym, "wert": None, "fcf": fcf, "fcf_basis": letzter,
                "basis_art": art, "bestimmtheit": r2,
                "tag_cashflow": tag_cf, "tag_investitionen": tag_inv,
                "grund": "freier Cashflow nur %.1f Prozent des Umsatzes - der Ausbau verbraucht, "
                         "was hereinkommt; die Rechnung haengt dann am Basisjahr und traegt "
                         "keine Aussage" % (100 * letzter / umsatz)}

    # Fortschreibung mit Abklingen: das Anfangswachstum faellt ueber zehn Jahre
    # linear auf das Endwachstum. Ohne Abklingen entstehen Werte, die eine Firma
    # groesser machen als ihren Markt.
    barwert, lauf = 0.0, letzter
    for j in range(1, JAHRE + 1):
        rate = w + (ENDWACHSTUM - w) * (j - 1) / (JAHRE - 1)
        lauf *= (1 + rate)
        barwert += lauf / (1 + ABZINSUNG) ** j
    endwert = lauf * (1 + ENDWACHSTUM) / (ABZINSUNG - ENDWACHSTUM)
    barwert_endwert = endwert / (1 + ABZINSUNG) ** JAHRE
    unternehmenswert = barwert + barwert_endwert

    _, geld, _ = _jahreswerte(f, TAGS["geld"], fluss=False)
    _, anlagen, _ = _jahreswerte(f, TAGS["anlagen"], fluss=False)
    _, lang, _ = _jahreswerte(f, TAGS["schulden_lang"], fluss=False)
    _, kurz, _ = _jahreswerte(f, TAGS["schulden_kurz"], fluss=False)

    def juengst(reihe):
        return reihe[max(reihe)] if reihe else 0.0

    nettoschulden = juengst(lang) + juengst(kurz) - juengst(geld) - juengst(anlagen)
    eigenkapitalwert = unternehmenswert - nettoschulden

    aktien = e.get("aktien_zahl")
    if not aktien:
        _, reihe, _ = _jahreswerte(f, TAGS["aktien"], fluss=False)
        aktien = juengst(reihe) or None
    if not aktien:
        return {"ticker": sym, "wert": None, "grund": "keine Aktienzahl"}

    return {
        "ticker": sym,
        "wert": eigenkapitalwert / aktien,
        "waehrung": einheit or "USD",
        "fcf": fcf,
        "fcf_basis": letzter,
        "basis_art": art,
        "bestimmtheit": r2,
        "wachstum": w,
        "endwertanteil": barwert_endwert / unternehmenswert,
        "unternehmenswert": unternehmenswert,
        "nettoschulden": nettoschulden,
        "aktien": aktien,
        "tag_cashflow": tag_cf,
        "tag_investitionen": tag_inv,
        "annahmen": {"abzinsung": ABZINSUNG, "endwachstum": ENDWACHSTUM, "jahre": JAHRE},
    }


def main():
    D, _ = b.daten_der_seite()
    F = D["firmen"]
    gewuenscht = [a.upper() for a in sys.argv[1:]] or list(F)
    raus = {}
    print("%-10s %14s %14s %8s %9s  %s" %
          ("Ticker", "innerer Wert", "Kurs", "Verh.", "Endwert%", "Investitions-Tag"))
    for sym in gewuenscht:
        if sym not in F:
            continue
        e = F[sym]
        erg = innerer_wert(sym, e)
        raus[sym] = erg
        if erg.get("wert"):
            kurs = e.get("kurs")
            verh = (kurs / erg["wert"]) if kurs and erg["wert"] else None
            print("%-10s %14.2f %14.2f %8s %8.0f%%  %s" %
                  (sym, erg["wert"], kurs or 0,
                   ("%.2f" % verh) if verh else "—",
                   100 * erg["endwertanteil"], erg.get("tag_investitionen") or "—"))
        else:
            print("%-10s %14s %14s %8s %9s  %s" % (sym, "—", "", "", "", erg["grund"][:60]))
    ziel = b._pfad("wert.json")
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    json.dump(raus, open(ziel, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\n-> %s" % ziel)


if __name__ == "__main__":
    main()
