# T2 Der Engpass liegt beim Angebot, nicht bei der Nachfrage

Stand 2026-11-21 · These Mendel · Status: **vorschlag** · Wiki: [no-standard-cycle-without-absorption-check](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/memory_supply/rules/no-standard-cycle-without-absorption-check.md), [demand-is-not-earnings](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/ai_demand_drivers/rules/demand-is-not-earnings.md)

## Aussage

Gelesen wird die schwerer zu widerlegende Fassung: Für KI-Speicher (HBM, Server-DRAM) begrenzt das Angebot die Menge, nicht die Nachfrage.

    Angebotsengpass  ⇔  bei geltenden Preisen Nachfrage > Angebot
                     ⇒  Vertragspreise ↑  ∧  Anzahlungen und Vorabverträge ↑  ∧  Herstellerlager ↓

## Was dafür spricht

| Beobachtung | Quelle | Tier |
|---|---|---|
| Micron-Kundenanzahlungen 0,57 → 12,9 Mrd USD | Micron-Bericht, Wiki micron-customer-deposits-jump | 1a |
| HBM-Menge 2027 vorab vertraglich gebunden | Fachpresse, Wiki second-source-hbm4-arrives-presold | 2 |
| TSMC: Nachfrage über Angebot, Lücke weiter groß | TSMC Q3-Call, Wiki tsmc-q3-2026-call-outlook | 1a, bis zum Transkript vorschlag |
| Q4 2026 Vertragspreise konv. DRAM +10 bis 15 % | [TrendForce](https://www.trendforce.com/presscenter/news/20260930-13258.html) | 2 |

Rechnung ([ergebnisse/02](../ergebnisse/02_schwelle_standard_dram.txt)): Konventionelles DRAM behält 2027 seine Wafer nur, wenn die Waferzufuhr um mehr als 11,4 % wächst. Mit HBM4-Aufschlag liegt die Schwelle bei 13,9 %. Bei 5 % Wafer-Wachstum verliert konventionelles DRAM 5,8 bis 7,8 % seiner Wafer. Bei den Bits sieht es anders aus: Sie wachsen schon, wenn alle DRAM-Bits um mehr als 4,6 % wachsen. Die Knappheit ist also eine Frage der Wafer, nicht unbedingt der Bits.

## Was dagegen spricht oder gemischt ist

- Die Q4-Zuwächse sind kleiner als in den Vorquartalen.
- Spot ist schwächer: DDR5 16Gb lag am 2026-11-13 bei 60,27 USD, +0,06 % zur Vorsitzung (TrendForce-Log im Wiki, Tier 2).
- PC-Lager steigen.

Lesart: Das passt zu einer geteilten Lage. Bei Server und HBM begrenzt das Angebot. Am Konsumrand stößt die Nachfrage über den Preis an ihre Grenze (Erschwinglichkeit). Dass die Zuwächse kleiner werden, widerlegt die These nicht. Widerlegt wäre sie, wenn die Zuwächse negativ werden.

## Stärkstes Gegenargument (≈ 25 %)

In der zweiten Jahreshälfte 2027 kommen neue Werke in Betrieb. Fällt gleichzeitig die Konsumnachfrage, holt das Angebot bei konventionellem DRAM auf, und der Engpass bleibt nur bei HBM. Für Speicheraktien wäre das ein halber Bruch, weil konventionelles DRAM der größere Teil der Bits ist.

## Wahrscheinlichkeit

Server-DRAM-Vertragspreise steigen in Q2 2027 noch gegenüber dem Vorquartal: etwa 70 %. Grundlage: Branchendienst und Firmenaussagen, keine eigene Messung der Lager.

## Bruchindikator

- Vertragspreise Server-DRAM fallen gegenüber dem Vorquartal.
- Herstellerlager in Wochen steigen zwei Quartale in Folge (Berichte und Calls).
- Micron-Kundenanzahlungen fallen.
- HBM-Verträge für 2028 schließen unter dem Preis je Bit von 2027.

## Nächste Prüfung

1. Lagerreichweite in Wochen je Hersteller aus den Q3-Berichten und Calls ablegen (SK hynix, Samsung, Micron FQ1 FY27 im Dez 2026).
2. Aus dem täglichen Wiki-Log `speicher_indikatoren_log.csv` eine Reihe Vertrag gegen Spot je Quartal bauen.
3. Werke mit Anlauf 2027 und ihre Waferzahl mit Quelle (Wiki-Prüfpunkt dram-wafer-capacity-by-fab). Damit wird die Schwelle von 11,4 % prüfbar.
