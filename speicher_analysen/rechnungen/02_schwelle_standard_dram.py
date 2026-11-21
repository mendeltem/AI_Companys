# These 1 und 2: Ab welchem Wachstum der gesamten DRAM-Waferzufuhr behaelt
# konventionelles DRAM 2027 seine Wafer? Und ab welchem Bitwachstum seine Bits?
#
#   konv. Wafer 2027 / 2026 = (1 + g) * (1 - s27) / (1 - s26)
#   Schwelle: g* = (1 - s26) / (1 - s27) - 1
#   konv. Bits 2027 / 2026  = (1 + G) * (1 - b27) / (1 - b26)
#   Schwelle: G* = (1 - b26) / (1 - b27) - 1
# g Wachstum der Waferzufuhr, G Wachstum aller DRAM-Bits.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

s26 = par["hbm_waferanteil_2026"]
s27 = par["hbm_waferanteil_2027"]
b26 = par["hbm_bitanteil_2026"]
b27 = par["hbm_bitanteil_2027"]
# Waferanteil 2027, wenn der Mix-Aufschlag aus 01 dazukommt (gleiche Rechnung wie dort)
w26 = (1 - par["hbm4_mix_ende_2026"]) * par["tausch_hbm3e"] + par["hbm4_mix_ende_2026"] * par["tausch_hbm4"]
w27 = (1 - par["hbm4_mix_2027"]) * par["tausch_hbm3e"] + par["hbm4_mix_2027"] * par["tausch_hbm4"]
r26 = s26 * (1 - b26) / (b26 * (1 - s26))
r27_mix = r26 * w27 / w26
s27_mix = b27 * r27_mix / (b27 * r27_mix + (1 - b27))

g_stern = (1 - s26) / (1 - s27) - 1
g_stern_mix = (1 - s26) / (1 - s27_mix) - 1
G_stern = (1 - b26) / (1 - b27) - 1
print(f"Waferschwelle: konventionelles DRAM behaelt seine Wafer nur, wenn die Waferzufuhr 2027 um mehr als "
      f"{g_stern:.1%} waechst ({1 - s26:.0%} / {1 - s27:.0%} - 1).")
print(f"  mit Mix-Aufschlag (HBM {s27_mix:.1%}): Schwelle {g_stern_mix:.1%}")
print(f"Bitschwelle: konventionelle Bits wachsen nur, wenn alle DRAM-Bits um mehr als {G_stern:.1%} wachsen.")
print()
print("Waferzufuhr g | konv. Wafer 2027 gg. 2026 | mit Mix-Aufschlag")
for g in [0.0, 0.03, 0.05, 0.08, g_stern, 0.15]:
    a = (1 + g) * (1 - s27) / (1 - s26) - 1
    b = (1 + g) * (1 - s27_mix) / (1 - s26) - 1
    print(f"  {g:6.1%}      | {a:+7.1%}                  | {b:+7.1%}")
print()
print("Bitwachstum G | konv. Bits 2027 | HBM-Bits 2027")
for G in [0.05, 0.10, 0.15, 0.20, 0.25]:
    konv = (1 + G) * (1 - b27) / (1 - b26) - 1
    hbm = (1 + G) * b27 / b26 - 1
    print(f"  {G:6.0%}      | {konv:+6.1%}          | {hbm:+6.1%}")
print()
print("Lesart: Fuer die Bits reicht schon eine kleine Zahl, die Wafer brauchen zweistellig.")
print("Die Waferzufuhr waechst nicht beliebig (ASML sieht 2027/28 eine Bestueckungsluecke);")
print("wo sie liegt, ist offen (Wiki dram-wafer-capacity-by-fab).")
