# These 1 nach 2030: Was 3D-DRAM mit dem HBM-Waferanteil und mit der
# Knappheit macht. Beide laufen dann auseinander.
#
#   Bits je Wafer gegen heutiges DRAM  f = Lagen / Lagen_Gleichstand
#   HBM-Waferanteil                    s = b*r / (b*r + (1 - b))
#   Wafer fuer dieselben Bits          W = b*r*w_hbm + (1 - b)*w_std   (heute = b*r + (1 - b))
#
# b HBM-Bitanteil, r Wafer je Bit HBM / Standard (relatives Tauschverhaeltnis),
# w Wafer je Bit gegen heute (1/f fuer die Klasse, die auf 3D umsteigt).
# Faelle: nur Standard-DRAM in 3D (HBM bleibt flach, weil gedünnte TSV-Dies
# mit hohem Zellstapel schwerer sind; eigene Einschaetzung, etwa 60 %) und
# beide in 3D. Ausgangspunkt sind die TrendForce-Werte fuer 2027.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

b = par["hbm_bitanteil_2027"]
s0 = par["hbm_waferanteil_2027"]
r0 = s0 * (1 - b) / (b * (1 - s0))
gleich = par["lagen_gleichstand_3d"]
W0 = b * r0 + (1 - b)
print(f"Ausgang 2027 (TrendForce): Bitanteil {b:.0%}, Waferanteil {s0:.0%}, r = {r0:.2f}")
print(f"Gleichstand 3D = {gleich:.0f} Lagen, erstes Produkt {par['lagen_erstes_3d_produkt']:.0f} Lagen")
print()
print("Lagen | Bits/Wafer | Fall                 |   r   | HBM-Waferanteil | Wafer fuer dieselben Bits | noetiges Bitwachstum fuer gleiche Knappheit")
for lagen in [100, 200, 300]:
    f = lagen / gleich
    for fall, w_hbm, w_std in [("nur Standard in 3D", 1.0, 1 / f), ("beide in 3D", 1 / f, 1 / f)]:
        r = r0 * w_hbm / w_std
        s = b * r / (b * r + (1 - b))
        W = (b * r0 * w_hbm + (1 - b) * w_std) / W0
        print(f"{lagen:5d} | x{f:4.2f}      | {fall:20s} | {r:5.2f} | {s:14.1%}  | {W:24.0%}  | x{1 / W:4.2f}")

print()
print("Lesart: Der HBM-Waferanteil kann mit 3D steigen (nur Standard in 3D), waehrend die Branche fuer")
print("dieselben Bits deutlich weniger Wafer braucht. Ein steigender Anteil zeigt dann keine Knappheit mehr an.")
print("Zweiter Messwert fuer T1 nach 2030:")
print("  Knappheitsgrad = Wafer-Aequivalente der Nachfrage / Waferkapazitaet")
print("  Wafer-Aequivalente = Bits_HBM * w_HBM + Bits_Standard * w_Standard (je Bauart und Lagenzahl)")
print("  Waferkapazitaet: Wiki-Pruefpunkt dram-wafer-capacity-by-fab, noch offen.")
