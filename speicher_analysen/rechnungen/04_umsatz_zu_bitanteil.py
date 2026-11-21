# These 3 und Pruefung p2: Samsung meldet fuer Q3 2026 HBM4 = 60 % des
# HBM-Umsatzes. Welcher Bitanteil folgt daraus?
#
# Umsatzanteil U = b*p / (b*p + (1 - b)), p = Preis je Bit HBM4 / HBM3E
#   -> b = U / (U + p*(1 - U))
#   -> p = U*(1 - b) / (b*(1 - U))
# Bit ist nicht Stueck: bei gleicher Stapelhoehe (12-Hi, 36 GB) sind Bits und
# Stapel gleich verteilt; ein 8-Hi-HBM3E-Stapel hat nur 24 GB.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

U = par["samsung_hbm4_umsatzanteil_q3_2026"]
p_forderung = par["preis_hbm4_ask_2027"] / par["preis_hbm3e_2027"]

print(f"Samsung Q3 2026: HBM4 = {U:.0%} des HBM-Umsatzes")
print("Preisverhaeltnis p | HBM4-Bitanteil")
for p in [1.0, 1.25, 1.5, 2.0, 2.5, p_forderung, 3.0]:
    b = U / (U + p * (1 - U))
    print(f"  {p:4.2f}             | {b:5.1%}")

p_kipp = U / (1 - U)
print(f"Kipppunkt: mehr HBM4- als HBM3E-Bits nur, wenn p unter {p_kipp:.2f} liegt.")
print(f"Fachpresse-Forderung 2027: {par['preis_hbm4_ask_2027']} gegen {par['preis_hbm3e_2027']} USD/Gb, p = {p_forderung:.2f}")

b_chat = par["hbm4_mix_ende_2026"]
p_noetig = U * (1 - b_chat) / (b_chat * (1 - U))
print(f"Damit Samsungs 60 % Umsatz zu einem Bitanteil von {b_chat:.0%} passen (Mix-Annahme Ende 2026), muesste p = {p_noetig:.2f} sein.")
print()
print("Lesart: 60 % Umsatz heissen nicht 60 % Stueck. Bei p zwischen 2 und 3 liegt Samsungs")
print("HBM4-Bitanteil bei 33 bis 43 %. Samsung ist zudem nicht die Branche: Samsung war bei HBM3E fuer")
print("Nvidia schwach, ein hoher HBM4-Anteil im eigenen Mix kann aus dem fehlenden HBM3E kommen.")
