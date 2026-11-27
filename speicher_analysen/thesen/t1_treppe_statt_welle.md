# T1 Treppe statt Welle

Stand 2026-11-21 · These Mendel · Status: **vorschlag** · Wiki: [hbm-generation-change-ratchets-cannibalisation](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/memory_supply/mechanisms/hbm-generation-change-ratchets-cannibalisation.md)

## Aussage

Jeder HBM-Generationswechsel hebt die Wafer-Kannibalisierung, danach fällt sie nicht zurück. Gleiches Muster bei Nvidia seit 2023.

Formal, mit C(t) = HBM-Anteil an der DRAM-Waferzufuhr und t_k = Generationswechsel k:

    Treppe  ⇔  ∀k: C(t_k + τ) > C(t_k − τ)  ∧  ∀t > t_k + τ_Ausbeute: C(t) ≥ C(t_k + τ_Ausbeute)
    Welle   ⇔  ∃k: C(t) < C(t_k − τ) für ein t nach dem Hochlauf

Eine Stufe hat zwei Teile: einen Ausbeuteteil, der abklingt, und einen strukturellen Teil (größeres Die, mehr TSVs, höheres Tauschverhältnis), der bleibt.

## Was die Rechnung zeigt

[ergebnisse/01](../ergebnisse/01_wafer_mix_menge.txt):

| Anteil am Schritt 2026 → 2027 | Punkte der DRAM-Wafer | Anteil |
|---|---|---|
| Menge (HBM-Bitanteil 9 → 13 %) | +8,0 | 84 % |
| Mix (HBM4 33 → 60 %, Verhältnis +8,1 %) | +1,5 | 16 % |
| zusammen | +9,5, also 31,5 % statt 22 % | |

Die 1,8 Punkte aus dem Chat gelten bei fester Waferzufuhr und festen HBM-Bits (Rahmung A). Mit festen Bitanteilen sind es 1,5 (Rahmung B, Shapley). Für das Ergebnis macht das keinen Unterschied.

Neu: TrendForce' eigene Anteile ergeben für 2026 und 2027 dasselbe Verhältnis (2,85 und 2,87). Ihre 30 % für 2027 enthalten also keinen HBM4-Aufschlag. Kommt er dazu, landet man bei 31,5 % (Prüfung [p1](../pruefungen/p1_tauschverhaeltnis.md)).

Nvidia ([ergebnisse/06](../ergebnisse/06_treppe_in_quartalen.txt), SEC-XBRL, Tier 1a): Gemessen am Umsatzzuwachs je Quartal ergibt sich eine Treppe.

| Abschnitt | Zuwachs je Quartal |
|---|---|
| Okt 2023 bis Apr 2025 (Hopper, frühes Blackwell) | 4,4 Mrd USD |
| Jul 2025 (Übergang) | +2,7 |
| Okt 2025 bis Jul 2026 (GB300) | 12,4 Mrd USD |
| Okt 2026 (Rubin beginnt) | +19,6 |
| Ausblick Jan 2027, auf 13 Wochen | +4,9 (nominal +14,2 mit 14 Wochen) |

Seit Jan 2023 ist der Umsatz in jedem Quartal gestiegen. Innerhalb einer Stufe fällt die Rate in Prozent von selbst (34 % auf 12 % bei fast gleichem Zuwachs). „Wachstum verlangsamt sich“ ist auf einer flachen Stufe also Arithmetik. Der Ausblick für Jan 2027 sieht aus wie der Übergang im Jul 2025.

## Trägt

- Die Richtung: Das strukturelle Tauschverhältnis steigt je Generation (Micron, Tier 1b über Fachpresse).
- Bei Nvidia lässt sich die Treppe in den Zuwächsen beschreibend aus Tier-1a-Zahlen ablesen.

## Trägt nicht

- Die Größe der Stufe aus dem Mix: Der Generationswechsel bringt rund ein Sechstel.
- Den Auslöser des aktuellen Preislaufs: DDR5 stieg ab Okt 2025, also vor dem HBM4-Hochlauf.
- Die Nvidia-Reihe als Beleg für die Speicherseite. Sie misst Umsatz, keine Wafer. Sie ist eine Parallele, die die Hypothese anregt, kein Beweis. Ob die Verlangsamung jeweils „angekündigt“ war (Ausblick oder Presse), ist nicht geprüft.

## Stärkstes Gegenargument (≈ 20 %)

Die Treppe besteht zu 84 % aus Menge, und gerade die Menge kann zurückfallen. Nur der strukturelle Teil, rund 16 %, rastet wirklich ein. Hält die KI-Nachfrage nicht (Finanzierungsgrenze, Capex-Pause), sinkt der HBM-Waferanteil trotz höherem Tauschverhältnis. Die These hängt damit an T2 und an den Wiki-Axiomen, nicht am Generationswechsel. Wahrscheinlichkeit, dass der HBM-Waferanteil Ende 2028 unter dem Stand von Ende 2026 (22 %) liegt: etwa 20 %. Grundlage dünn: ein Branchendienstpfad und eine Firmenaussage.

## Bruchindikator

- Konventionelle Vertragspreise steigen beim nächsten Wechsel (HBM4E, 16-Hi) nicht stufig, obwohl die Servernachfrage nicht langsamer wächst.
- Ein Hersteller weist Waferstarts je Produktklasse aus, und der HBM-Anteil fällt nach dem Hochlauf zurück.
- Die Waferzufuhr 2027 wächst um mehr als 11,4 % ([ergebnisse/02](../ergebnisse/02_schwelle_standard_dram.txt)).
- Nvidia: Liegen die Zuwächse in den Quartalen bis Apr und Jul 2027 beide unter 12,4 Mrd USD, ist es bei Nvidia eine Welle.

## Nächste Prüfung

1. Nvidia GJ2027 Q4 (Feb 2027) und GJ2028 Q1 (Mai 2027) in `quartale.csv` nachtragen, `06` neu laufen lassen.
2. Ausblick gegen Ist für jedes Nvidia-Quartal seit 2023 ablegen (Pressemitteilungen, Tier 1a). Damit lässt sich „angekündigt“ prüfen.
3. Prüfung p1 klären: Danach steht fest, ob der HBM-Waferanteil 2027 bei 30 oder bei 31,5 bis 35 % liegt.

## Nach 2030: 3D-DRAM (Stand 2026-11-26)

Anlass: SK hynix strebt 3D-DRAM mit 100 Zelllagen in vier bis fünf Jahren an, also um 2031. Die Dichte des heutigen 10-nm-DRAM erreicht 3D bei etwa 75 Lagen (Vortrag eines SK-hynix-Ingenieurs, The Elec 2026-11-25, Tier 1b über 2). Für 200 bis 300 Lagen braucht es eigene Maschinen.

Thesenzusatz Mendel: Die HBM-Kannibalisierung steigt auch mit 3D-DRAM weiter.

Rechnung ([ergebnisse/11](../ergebnisse/11_3d_dram_wafer.txt)), Ausgang TrendForce 2027 (Bitanteil 13 %, Waferanteil 30 %, r = 2,87):

| Lagen | Bits je Wafer | Fall | HBM-Waferanteil | Wafer für dieselben Bits | nötiges Bitwachstum für gleiche Knappheit |
|---|---|---|---|---|---|
| 100 | ×1,33 | nur Standard in 3D | 36 % | 82 % | ×1,21 |
| 100 | ×1,33 | beide in 3D | 30 % | 75 % | ×1,33 |
| 200 | ×2,67 | nur Standard in 3D | 53 % | 56 % | ×1,78 |
| 200 | ×2,67 | beide in 3D | 30 % | 38 % | ×2,67 |
| 300 | ×4,00 | nur Standard in 3D | 63 % | 48 % | ×2,11 |
| 300 | ×4,00 | beide in 3D | 30 % | 25 % | ×4,00 |

Trägt: Der Thesenzusatz in der Richtung. Steigt der HBM-Bitanteil weiter, steigt der Waferanteil. Wechselt Standard-DRAM früher auf 3D als HBM, steigt er sogar schneller. Eigene Einschätzung: etwa 60 %, weil gedünnte HBM-Dies mit TSVs und hohem Zellstapel schwerer zu fertigen sind.

Trägt nicht: Knappheit aus dem Anteil allein. Mit 3D laufen beide auseinander. Der Anteil kann von 30 auf über 50 % steigen, während die Branche für dieselben Bits nur noch etwa die Hälfte der Wafer braucht. Für Preise zählt die Waferkapazität gegen die Wafernachfrage, nicht der Anteil.

Deshalb nach 2030 ein zweiter Messwert neben dem Waferanteil:

    Knappheitsgrad = Wafer-Äquivalente der Nachfrage / Waferkapazität
    Wafer-Äquivalente = Bits_HBM · w_HBM + Bits_Standard · w_Standard   (je Bauart und Lagenzahl)

Die Waferkapazität ist der offene Wiki-Prüfpunkt `dram-wafer-capacity-by-fab`.

Zeitbezug: Für 2027 bis 2029 ändert 3D-DRAM nichts. Dass 3D-DRAM bis Ende 2031 in Serie geht, schätze ich auf etwa 50 %. Bei 3D-NAND lagen zwischen Ankündigung (2007) und Serie (2013) etwa sechs Jahre.

Bruchindikator für den Zusatz: Ein Hersteller bringt HBM auf 3D-Kerndies vor oder gleichzeitig mit Standard-DRAM. Dann bleibt r gleich und der Anteil steigt nur noch über die Menge.

Frühe Signale: Beschluss einer 3D-DRAM-Pilotlinie mit Budget (DART), Bestellungen eigener Stapel- und Ätzmaschinen, ein erstes Produkt mit Kunde.

## Quellen

| Angabe | Quelle | Tier |
|---|---|---|
| Tauschverhältnis 3 / gegen 4 | Micron über TrendForce News, Hot Chips 2026 | 1b über 2 |
| Wafer- und Bitanteile | TrendForce | 2 |
| HBM nahe 30 % der Waferkapazität 2027 | Samsung EVP Kim Taewoo über Reuters, 2026-09-29 | 1b über 2 |
| Nvidia-Quartale | SEC-XBRL, Q3 GJ2027 Pressemitteilung 2026-11-17 | 1a |
| HBM4-Mix 33 / 60 % | Chat 2026-11-21, Herkunft nicht vermerkt | offen |
| 3D-DRAM: 75 Lagen Gleichstand, 100 Lagen erstes Produkt, ~2031 | [The Elec, 2026-11-25](https://www.thelec.net/news/articleView.html?idxno=15925), Vortrag SK-hynix-Ingenieur | 1b über 2 |
