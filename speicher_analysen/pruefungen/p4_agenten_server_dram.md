# P4 Anteil der Agenten am Server-DRAM

Stand 2026-11-21 · Status: **offen, Messgrößen festgelegt** · Rechnung: [ergebnisse/08](../ergebnisse/08_cpu_dram_je_gpu.txt)

## Messgrößen

Die Rechnung zeigt: CPU:GPU-Verhältnis und Speicher je CPU-Knoten wirken nur als Produkt. Gemessen werden deshalb zwei Größen.

| Messgröße | Was sie trennt | Quelle | Tier |
|---|---|---|---|
| M1 CPU-DRAM je GPU im Rack | Vera-Konfiguration × CPU:GPU | OEM-Datenblätter der ausgelieferten Vera-Rubin-Systeme, Nvidia | 1b |
| M2 DRAM in eigenständigen CPU-Servern je installierter GPU (X) | Agenten- und Sandkasten-Server außerhalb des Racks | Server-Stückzahlen × DRAM je Server (IDC, TrendForce) gegen GPU-Bestand | 2 |

Ersatzgrößen für M2, solange es keine direkte Zahl gibt:
- CPU-Umsatz im Rechenzentrum: Intel DCAI, AMD Data Center (CPU-Teil), Nvidia CPU-Umsatz (Ausblick „mehr als doppelt im GJ2028“). Tier 1a.
- Kommentare der Hyperscaler zu allgemeinen Servern in den Calls (Capex-Aufteilung). Tier 1a.
- Hersteller-Mix: Server-DDR5-Module ab 128 GB (SK hynix, Micron). Tier 1a.

## Kippwerte aus der Rechnung

Bei 750 GB CPU-DRAM je GPU zieht konventionelles DRAM mit HBM gleich, sobald X über 402 GB je GPU liegt. Bei 375 GB je GPU liegt der Kippwert bei 777 GB. Eine grobe Lage von M1 und M2 genügt also, um T5 zu entscheiden. Genaue Zahlen braucht es dafür nicht.

## Abschluss

Erledigt, wenn M1 aus einem Datenblatt stammt und M2 als Spanne aus mindestens einer Ersatzgröße mit Tier 1a vorliegt. Dann in `daten/parameter.csv` eintragen und `08` anpassen.
