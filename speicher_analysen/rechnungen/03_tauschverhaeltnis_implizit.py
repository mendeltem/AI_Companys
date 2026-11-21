# Pruefung p1: TrendForce-Anteile ergeben ein Tauschverhaeltnis von etwa 2,9
# fuer 2026 und 2027, Micron nennt 3 (HBM3E) bis 4 (HBM4). Warum?
#
# r_TF = (s / (1 - s)) / (b / (1 - b))    Waferanteil s, Bitanteil b
# r_TF misst HBM gegen den Durchschnitt aller konventionellen Wafer.
# Micron misst HBM gegen DDR5, vermutlich im selben Knoten. Liegt der
# konventionelle Durchschnitt um den Faktor k unter der Dichte des
# HBM-Knotens (aeltere Knoten, DDR4, LPDDR4), gilt r_TF = r_Micron / k.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

t3 = par["tausch_hbm3e"]
t4 = par["tausch_hbm4"]
m26 = par["hbm4_mix_ende_2026"]
m27 = par["hbm4_mix_2027"]

def r_aus(s, b):
    return (s / (1 - s)) / (b / (1 - b))

# 1. Punktwerte
r26 = r_aus(par["hbm_waferanteil_2026"], par["hbm_bitanteil_2026"])
r27 = r_aus(par["hbm_waferanteil_2027"], par["hbm_bitanteil_2027"])
print(f"1. TrendForce-implizit: 2026 r = {r26:.2f}, 2027 r = {r27:.2f}")

# 2. Rundung: TrendForce nennt ganze Prozent. Wie weit traegt die Rundung?
lo26 = r_aus(0.215, 0.095)
hi26 = r_aus(0.225, 0.085)
lo27 = r_aus(0.295, 0.135)
hi27 = r_aus(0.305, 0.125)
print(f"2. Rundungsband (Anteile +-0,5 Punkte): 2026 {lo26:.2f} bis {hi26:.2f}, 2027 {lo27:.2f} bis {hi27:.2f}")
print(f"   Micron im Mix: 2026 {(1 - m26) * t3 + m26 * t4:.2f}, 2027 {(1 - m27) * t3 + m27 * t4:.2f}")
print("   -> Rundung erklaert die Luecke nicht.")

# 3. Bezugsbasis: welcher Dichteabstand k macht beide Angaben vereinbar?
rm26 = (1 - m26) * t3 + m26 * t4
rm27 = (1 - m27) * t3 + m27 * t4
k26 = rm26 / r26
k27 = rm27 / r27
print(f"3. Noetiger Dichteabstand k = r_Micron / r_TF: 2026 {k26:.2f}, 2027 {k27:.2f}")
print(f"   Der konventionelle Durchschnitt muesste 2026 {k26 - 1:.0%} weniger Bits je Wafer liefern als der HBM-Knoten,")
print(f"   2027 {k27 - 1:.0%}. Der Abstand muesste also wachsen: HBM zieht im Knoten davon (HBM4 auf 1c),")
print("   oder TrendForce rechnet den Mix-Aufschlag nicht ein.")

# 4. Untergrenze ohne Mix: nur HBM3E zu 3
k_nur3 = t3 / r26
print(f"4. Selbst mit reinem HBM3E (3,0) braucht 2026 einen Abstand von {k_nur3 - 1:.0%}.")

# 5. Was 4:1 als Durchschnitt hiesse
for r in [3.33, 3.6, 4.0]:
    b = par["hbm_bitanteil_2027"]
    s = b * r / (b * r + (1 - b))
    print(f"5. Bei r = {r:.2f} und Bitanteil {b:.0%} waere der Waferanteil 2027 {s:.1%} statt 30 %")

print()
print("Pruefbare Folgerung: Nennt Micron die Bezugsbasis (gleicher Knoten oder Flottenschnitt),")
print("ist Hypothese 3 entschieden. Nennt TrendForce den HBM4-Anteil hinter den 30 %, ist Hypothese 5 entschieden.")
