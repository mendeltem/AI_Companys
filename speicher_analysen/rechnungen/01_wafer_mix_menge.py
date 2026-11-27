# These 1 (Treppe): Wie viel vom Anstieg des HBM-Waferanteils kommt aus dem
# Generationswechsel HBM3E -> HBM4 (Mix), wie viel aus der HBM-Bitmenge?
#
# Zwei Rahmungen, beide werden gerechnet:
#   A  feste Waferzufuhr, feste HBM-Bits: wie viele Punkte aller DRAM-Wafer
#      braucht HBM zusaetzlich, nur weil der Mix teurer wird? (Rahmung im Chat)
#   B  Anteilsformel mit TrendForce-Bitanteilen und einem relativen
#      Tauschverhaeltnis r (HBM-Wafer je Bit / konventionelle Wafer je Bit):
#          s = b*r / (b*r + (1 - b))
#      s Waferanteil HBM, b Bitanteil HBM. Zerlegung nach Shapley, also
#      Mittel aus beiden Reihenfolgen, damit nichts uebrig bleibt.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

t3 = par["tausch_hbm3e"]
t4 = par["tausch_hbm4"]
m26 = par["hbm4_mix_ende_2026"]
m27 = par["hbm4_mix_2027"]
s26 = par["hbm_waferanteil_2026"]
s27 = par["hbm_waferanteil_2027"]
b26 = par["hbm_bitanteil_2026"]
b27 = par["hbm_bitanteil_2027"]

# Wafer je HBM-Bit im Mix (DDR5 = 1)
w26 = (1 - m26) * t3 + m26 * t4
w27 = (1 - m27) * t3 + m27 * t4
mix = w27 / w26 - 1
print(f"Wafer je HBM-Bit: {w26:.3f} bei {m26:.0%} HBM4, {w27:.3f} bei {m27:.0%} HBM4, Mix-Aufschlag {mix:+.1%}")

# Rahmung A
punkte_a = s26 * mix
print(f"A  feste Wafer, feste HBM-Bits: HBM braucht {punkte_a * 100:.2f} Punkte aller DRAM-Wafer mehr "
      f"(Anteil {s26:.0%} -> {(s26 + punkte_a):.1%} der alten Zufuhr)")

# Rahmung B: relatives Tauschverhaeltnis aus TrendForce
def anteil(b, r):
    return b * r / (b * r + (1 - b))

def r_aus(s, b):
    return s * (1 - b) / (b * (1 - s))

r26 = r_aus(s26, b26)
r27_tf = r_aus(s27, b27)
r27_mix = r26 * (1 + mix)
print(f"B  TrendForce-implizit: r = {r26:.2f} (2026), {r27_tf:.2f} (2027); mit Mix-Aufschlag waere r 2027 = {r27_mix:.2f}")

basis = anteil(b26, r26)
nur_menge = anteil(b27, r26)
nur_mix = anteil(b26, r27_mix)
beides = anteil(b27, r27_mix)
menge = 0.5 * ((nur_menge - basis) + (beides - nur_mix))
mixeff = 0.5 * ((nur_mix - basis) + (beides - nur_menge))
print(f"   Waferanteil 2026 {basis:.1%}")
print(f"   nur Menge (Bitanteil {b26:.0%} -> {b27:.0%}, r fest): {nur_menge:.1%}")
print(f"   nur Mix (Bitanteil fest, r {r26:.2f} -> {r27_mix:.2f}):  {nur_mix:.1%}")
print(f"   beides: {beides:.1%}   (TrendForce nennt {s27:.0%})")
print(f"   Shapley: Menge {menge * 100:+.2f} Punkte, Mix {mixeff * 100:+.2f} Punkte, Summe {(beides - basis) * 100:+.2f}")

print()
print("Lesart:")
print(f"  TrendForce' eigene Zahlen ergeben r {r26:.2f} -> {r27_tf:.2f}, also keinen Mix-Effekt im Verhaeltnis.")
print(f"  Ihre {s27:.0%} fuer 2027 sind damit reine Menge ({(nur_menge - basis) * 100:.1f} Punkte).")
print(f"  Steigt das Verhaeltnis wie bei Micron, kaeme der Mix obendrauf: {beides:.1%} statt {s27:.0%}.")
print(f"  Die Treppe 2026 -> 2027 besteht zu rund {menge / (beides - basis):.0%} aus Menge.")
