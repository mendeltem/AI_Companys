# T3 Nvidia und AMD kaufen so viel HBM wie möglich, 2027 mehr HBM4 als HBM3E

Stand 2026-11-21 · These Mendel · Status: **vorschlag** · Wiki: [hbm-market-share-and-nvidia-allocation](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/memory_supply/open_checks/hbm-market-share-and-nvidia-allocation.md), [second-source-hbm4-arrives-presold](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/memory_supply/mechanisms/second-source-hbm4-arrives-presold.md)

## Aussage

    (Nvidia ∧ AMD kaufen bis zur Lieferobergrenze)  ∧  HBM4-Bitanteil 2027 > HBM3E-Bitanteil 2027

Zu klären ist, was „mehr“ misst: Bits, Stapel oder Umsatz. Und ob das ganze Jahr gemeint ist oder der Stand am Jahresende.

## Was die Rechnung zeigt

[ergebnisse/04](../ergebnisse/04_umsatz_zu_bitanteil.txt): Samsungs HBM4 = 60 % des HBM-Umsatzes in Q3 2026 heißt nicht 60 % der Bits.

| HBM4-Preis je Bit / HBM3E | HBM4-Bitanteil bei Samsung |
|---|---|
| 1,5 | 50 % (Kipppunkt) |
| 2,0 | 43 % |
| 2,67 (Fachpresse-Forderung 2027) | 36 % |
| 3,0 | 33 % |

Mehr HBM4- als HBM3E-Bits gibt es bei Samsung nur, wenn HBM4 je Bit weniger als das 1,5-Fache kostet. Die Mix-Annahme aus dem Chat (33 % HBM4 Ende 2026) passt zu Samsungs 60 % Umsatz, wenn das Preisverhältnis bei 3,05 liegt. Samsung ist nicht die Branche: Bei HBM3E für Nvidia war Samsung schwach. Ein hoher HBM4-Anteil im eigenen Mix kann daher kommen, dass HBM3E fehlt.

## Wer 2027 auf HBM3E bleibt

- GB300 läuft bis in 2027 weiter. Rubin-Racks kommen laut Wiki Feb bis Apr 2027 (gb300-ramp-timing-and-rubin-handover).
- ASICs: TPU v7 192 GB HBM3E, Trainium3 144 GB HBM3E, MI355X 288 GB HBM3E (Wiki custom-asics-use-hbm, Tier 1b, nicht gegen die Primärquelle geprüft).

## Wahrscheinlichkeit

- HBM4 über 50 % der HBM-Bits im Gesamtjahr 2027: etwa 55 %.
- HBM4 über 50 % der HBM-Bits in Q4 2027: etwa 80 %.

Grundlage dünn: Es gibt keine belastbare Stückquelle (Prüfung [p2](../pruefungen/p2_stueckanteile_hbm4_hbm3e.md)). Der Abstand zwischen Gesamtjahr und Jahresende ist der eigentliche Befund: Die These hält eher für den Ausstieg aus 2027 als für das Jahresmittel.

## „So viel wie möglich“

Dafür sprechen: Nvidia mit über 50 % des HBM (Wiki, Branchendienst), AMD mit 432 GB je MI450 (Wiki, Tier 1b) und eine angebliche Preisspitze bei HBM4 von +121 % in einer Woche (tech-insider.org, Tier 3, nur Spur). Dagegen spricht: Rubin Ultra wurde von 1 TB auf 384 GB und dann auf 256 GB gemeldet (KeyBanc, Wiki). Kauft man so viel wie möglich, ist die Menge je GPU durch das Angebot gedeckelt, und dann ist T3 eigentlich T2.

## Bruchindikator

- SK hynix oder Micron melden für 2027 einen HBM4-Anteil an den HBM-Bits unter 50 %.
- Nvidia meldet für 2027 hohe B300-Mengen neben Rubin.
- HBM3E-Preise je Bit steigen 2027 schneller als HBM4-Preise: Dann ist HBM3E der Engpass, nicht HBM4.

## Nächste Prüfung

Siehe [p2](../pruefungen/p2_stueckanteile_hbm4_hbm3e.md).
