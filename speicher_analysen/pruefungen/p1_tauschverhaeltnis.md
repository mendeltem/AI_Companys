# P1 TrendForce ergibt 2,9:1, Micron sagt 4:1. Warum?

Stand 2026-11-21 · Status: **offen, eingegrenzt** · Rechnung: [ergebnisse/03](../ergebnisse/03_tauschverhaeltnis_implizit.txt)

## Warum es zählt

Davon hängt ab, ob der HBM-Waferanteil 2027 bei 30 % liegt (TrendForce) oder bei 31,5 bis 35 %. Die Schwelle für konventionelles DRAM verschiebt sich dann von 11,4 auf 13,9 % Waferwachstum oder höher ([ergebnisse/02](../ergebnisse/02_schwelle_standard_dram.txt)).

## Stand der Rechnung

    r_TF = (s / (1 − s)) / (b / (1 − b))   →   2026: 2,85    2027: 2,87
    Micron im Mix (33 % bzw. 60 % HBM4):     2026: 3,33    2027: 3,60

| Hypothese | Prüfung hier | Ergebnis |
|---|---|---|
| H1 Rundung der ganzen Prozent | Anteile ±0,5 Punkte | **verworfen**: Band 2,61 bis 3,13 (2026), 2,68 bis 3,07 (2027), unter 3,33 |
| H2 Bezugsbasis: Micron misst gegen DDR5 im selben Knoten, TrendForce gegen den Flottenschnitt | nötiger Dichteabstand k = r_Micron / r_TF | **plausibel**: 2026 genügt k = 1,17, also 17 % weniger Bits je Wafer im Flottenschnitt |
| H3 Wachsender Knotenabstand | k müsste 2026 → 2027 von 1,17 auf 1,26 steigen | **offen**: verlangt, dass HBM im Knoten davonzieht (HBM4 auf 1c), schneller als konventionelles DRAM |
| H4 TrendForce rechnet den Mix-Aufschlag nicht ein | gleiches r in beiden Jahren | **offen, naheliegend**: dann ist 2027 eher 31,5 % |
| H5 Ausbeutegewinne senken das effektive Verhältnis von HBM3E | ohne Daten | offen |
| H6 Stichtage verschieden (Waferkapazität am Jahresende, Bits im Jahresmittel) | Richtung | macht die Lücke **größer**: Bei Wachstum liegt der Anteil am Jahresende über dem Mittel, das wahre r läge also noch tiefer |

H2 erklärt das Niveau, H3 oder H4 die gleichbleibende Höhe. Beide braucht man zusammen.

## Was die Frage entscheidet

1. Micron nennt die Bezugsbasis des Tauschverhältnisses (Call-Transkript, Investor Day, Hot-Chips-Folie). Gleicher Knoten bestätigt H2.
2. TrendForce nennt den HBM4-Anteil, der in den 30 % steckt. Nennt sie keinen, stützt das H4.
3. Knotenmix konventionelles DRAM 2026/2027 (1a/1b/1c-Anteile), etwa aus den Calls von SK hynix und Samsung, entscheidet H3.

## Quellen

TrendForce über [DRAMeXchange](https://dramexchange.com/WeeklyResearch/PrinterFriendly/2/12718.html) (Tier 2, Link aus dem Wiki). Micron über Fachpresse (1b über 2, Link im Chat nicht vermerkt).
