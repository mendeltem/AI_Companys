# T5 Server-DRAM steigt wegen Agenten

Stand 2026-11-21 · These Mendel · Status: **vorschlag** · Wiki: [cpu-attached-lpddr-adds-conventional-dram-demand](https://github.com/mendeltem/blackbeard_wikki/blob/main/knowledge/memory_supply/mechanisms/cpu-attached-lpddr-adds-conventional-dram-demand.md)

## Aussage

Agenten laufen zu einem großen Teil auf CPUs: Werkzeugaufrufe, Sandkästen, Browser, RL-Umgebungen. Dazu kommt KV-Cache, der in den CPU-Speicher ausgelagert wird. Beides treibt konventionelles Server-DRAM, zusätzlich zum HBM.

## Was die Rechnung zeigt

[ergebnisse/08](../ergebnisse/08_cpu_dram_je_gpu.txt): Waferäquivalent je GPU = HBM × Tauschverhältnis + CPU-DRAM je GPU + X (eigenständige Agenten-Server, auf die GPU umgelegt).

Die beiden Messgrößen aus dem Chat, CPU:GPU-Verhältnis und Speicher je CPU-Knoten, wirken nur als Produkt. Für den Rack-Teil reicht also eine Messgröße: **CPU-DRAM je GPU**. X ist die zweite Messgröße und davon getrennt.

| CPU-DRAM je GPU | X = 0 | Gleichstand mit HBM ab |
|---|---|---|
| 375 GB (Vera, halbes SOCAMM, 1:2) | konventionell 25 % | X = 777 GB je GPU |
| 750 GB (Vera 1,5 TB, 1:2) | konventionell 39 % | X = 402 GB je GPU |
| 1.500 GB (Vera 1,5 TB, 1:1) | konventionell 57 % | schon ohne X |

Gegen B300 (1.104 GB-Äquivalent) liegt Rubin je GPU um 38 bis 140 % höher, ohne Agenten-Server.

## Trägt

- Die Richtung: Pro GPU wächst der konventionelle Teil schneller als der HBM-Teil.
- Belege: Nvidia-CFO erwartet mehr als doppelten CPU-Umsatz im GJ2028 (Call, über Fachpresse, 1a über 2). SK hynix 3Q25: Server-DDR5 ab 128 GB mehr als verdoppelt gegenüber dem Vorquartal (1a).

## Trägt nicht

- Den Agentenanteil. Er ist nicht direkt messbar. X ist hier frei gesetzt, als Spannweite und nicht als Schätzung.
- Ausgelieferte Mengen. Die Vera-Konfiguration ist offen (TrendForce Juni 2026: SOCAMM halbiert).

## Wahrscheinlichkeit

Aus dem Wiki übernommen (2026-10-17): CPU-seitiges Server-DRAM über alle Anbieter ist 2027 ein Haupttreiber der konventionellen Knappheit, etwa 60 %. Eine neue Grundlage gibt es nicht. Prüfung [p4](../pruefungen/p4_agenten_server_dram.md).

## Bruchindikator

- Vera wird als Standard mit 750 GB oder weniger ausgeliefert.
- Intel DCAI und AMD Data Center (CPU-Teil) wachsen 2027 nicht schneller als 2025.
- Der DRAM-Gehalt je Server bleibt flach.

## Nächste Prüfung

Siehe [p4](../pruefungen/p4_agenten_server_dram.md).
