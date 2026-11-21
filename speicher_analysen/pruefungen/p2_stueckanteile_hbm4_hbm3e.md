# P2 Stückanteile HBM4 gegen HBM3E in Q4 2026

Stand 2026-11-21 · Status: **offen, keine belastbare Quelle** · Rechnung: [ergebnisse/04](../ergebnisse/04_umsatz_zu_bitanteil.txt)

## Warum es zählt

Der Mix-Effekt in T1 und die Aussage „2027 mehr HBM4 als HBM3E“ in T3 hängen am Bitanteil. Bisher gibt es nur den Umsatzanteil (Samsung 60 %) und eine Mix-Annahme ohne Herkunft (33 % Ende 2026, 60 % 2027).

## Was gemessen werden muss

Es geht um drei verschiedene Größen. Sie dürfen nicht vermischt werden:

| Größe | Umrechnung | Fallstrick |
|---|---|---|
| Umsatzanteil | Bitanteil = U / (U + p · (1 − U)) | p = Preis je Bit HBM4 / HBM3E, bisher nur Forderungspreise (2,67) |
| Bitanteil | die Größe, die für Wafer zählt | |
| Stapelanteil | Bits / GB je Stapel | HBM3E 8-Hi hat 24 GB, 12-Hi hat 36 GB; HBM4 12-Hi hat 36 GB |

## Quellen, die die Frage entscheiden

1. SK hynix Q3-2026-Call: HBM4-Anteil an den HBM-Lieferungen (Bits) und Plan für 2027 (Tier 1a). Der Bericht ist in dieser Umgebung nicht abrufbar, siehe [p5](p5_skhynix_q3_gegen_bericht.md).
2. Samsung Q3-2026-Call: Bezieht sich die 60 % auf Umsatz oder auf Bits? Welcher Anteil entfällt auf Nvidia?
3. Micron FQ1 FY2027 (Dez 2026): HBM4-Anteil, falls genannt.
4. TrendForce-HBM-Bericht: HBM4-Bitanteil Q4 2026 und 2027 (Tier 2, als Warnsignal).
5. Herkunft der Mix-Annahme 33 / 60 % aus dem Chat nachtragen.

## Abschluss

Die Prüfung ist erledigt, wenn zwei Hersteller einen Bit- oder Stückanteil für Q4 2026 oder für 2027 nennen. Dann `daten/parameter.csv` (hbm4_mix_*) ersetzen und `01` bis `04` neu laufen lassen.
