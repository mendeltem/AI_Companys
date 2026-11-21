# T4 Mehr Bandbreite → mehr Tokens pro Watt → Aufrüstzwang, auch wegen Platz

Stand 2026-11-21 · These Mendel · Status: **vorschlag** · Wiki: [bandwidth-bottleneck](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/ai_demand_drivers/axioms/bandwidth-bottleneck.md), [hbm-gb-per-mw-three-generations](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/ai_demand_drivers/findings/hbm-gb-per-mw-three-generations.md), [refresh-instead-of-new-build](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/ai_demand_drivers/mechanisms/refresh-instead-of-new-build.md)

## Aussage

    Bandbreite/W ↑  →  Tokens/W ↑   (gilt, wenn Decode bandbreitengebunden ist)
    fester Strom ∧ feste Fläche  →  Ausstoß ∝ Tokens/W
    Tausch lohnt  ⇔  (f − 1) · Erlös je MW-Jahr · Restjahre  >  Capex neu je MW − Restwert alt je MW

## Was die Rechnung zeigt

[ergebnisse/07](../ergebnisse/07_bandbreite_je_watt.txt), B300 gegen Rubin je GPU:

| | B300 | Rubin 22 TB/s | Rubin 19,2 TB/s |
|---|---|---|---|
| TB/s je kW | 5,71 | 12,22 | 10,67 |
| Faktor Bandbreite je W | | 2,14 | 1,87 |
| Anteil am 5,4-fachen Gewinn je MW (SemiAnalysis), log | | 45 % | 37 % |
| Anteil am 10-fachen Gewinn je MW (Nvidia), log | | 33 % | 27 % |

Die Bandbreite je Watt erklärt also ein gutes Viertel bis knapp die Hälfte des Gewinns je MW. Der größere Teil kommt aus Rechenformat, NVLink, Batching und Software.

Für den Speichermarkt zählt außerdem: Je MW verbaut Rubin 22 % weniger HBM-Kapazität als B300 (160.000 gegen 205.714 GB). Mit dem höheren Tauschverhältnis gerechnet, sind die HBM-Wafer je MW fast gleich (+3,7 %). Wer bei festem Strom tauscht, kauft mehr Bandbreite und teurere Bits, aber nicht mehr Wafer. Mehr Wafer kommen nur über mehr MW, mehr GB je GPU (Rubin Ultra) oder den CPU-Speicher ([T5](t5_server_dram_agenten.md)).

## Trägt

- Die Richtung der Kette bis Tokens/W.
- Der Aufrüstzwang bei festem Strom als Rechenregel: Tokens je MW steigen um das 5,4- bis 10-Fache, bei voller Auslastung also auch der mögliche Erlös je MW.

## Trägt nicht

- Bandbreite als Hauptursache des Gewinns: Sie ist der kleinere Teil.
- Mehr HBM-Bits durch Tausch: Je MW sind es weniger Bits, die Wafer bleiben fast gleich.
- Die Aufrüstschwelle in USD. Eingaben fehlen mit Quelle: Rack-Preis Rubin je MW, Erlös je MW-Jahr und Restwert von Blackwell.
- „Platz“ als eigene Grenze. Er lässt sich hier nicht vom Strom trennen. Bei gleicher Rackdichte je kW fallen beide zusammen.

## Bruchindikator

- Unabhängige Messungen zeigen für Rubin weniger als das 3-Fache je MW.
- Betreiber verlängern die Nutzungsdauer von Blackwell ohne Tausch (Abschreibungsdauer steigt, Tauschquote fällt).
- Tokenpreise fallen schneller, als die Tokens je MW steigen: Dann entfällt der Zwang.

## Nächste Prüfung

1. Die Quelle der Senkung auf 19,2 TB/s ablegen (bisher nur Chat).
2. Rubin-TDP von Nvidia bestätigen (bisher ~1.800 W aus dem Wiki).
3. Für die Aufrüstschwelle: Rack-Preis je MW (OEM-Angaben, Tier 1b) und Restwert (Wiki used-accelerator-and-workstation-prices).
