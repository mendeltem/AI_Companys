# These 5 und Pruefung p4: Server-DRAM steigt wegen Agenten.
#
# Waferaequivalent je GPU in GB Standard-DRAM (Faktoren wie im Wiki-Eintrag
# cpu-attached-lpddr-adds-conventional-dram-demand: HBM3E 3, HBM4 4, LPDDR 1):
#   W = HBM_GB x Tausch + CPU_DRAM_GB / GPU_je_CPU + X
# X = DRAM in eigenstaendigen CPU-Servern fuer Agenten, umgelegt je GPU.
#
# Die beiden Messgroessen aus dem Chat (CPU:GPU-Verhaeltnis, Speicher je
# CPU-Knoten) wirken nur als Produkt: CPU-DRAM je GPU. Eine Messgroesse
# reicht also fuer den Rack-Teil. X ist die zweite, getrennte Messgroesse.

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

b300 = par["hbm_gb_b300"] * par["tausch_hbm3e"] + par["lpddr_gb_grace"] / par["gpu_je_cpu_nvl72"]
print(f"B300 (GB300 NVL72): {par['hbm_gb_b300']:.0f} x {par['tausch_hbm3e']:.0f} + {par['lpddr_gb_grace']:.0f} / {par['gpu_je_cpu_nvl72']:.0f} = {b300:,.0f} GB-Aequivalent je GPU")
print()
hbm_rubin = par["hbm_gb_rubin"] * par["tausch_hbm4"]
print("Rubin: CPU-DRAM je GPU | X Agenten-Server je GPU | gesamt | gg. B300 | konventionell am Gesamt")
for cpu_je_gpu in [375, 750, 1500]:
    for x in [0, 250, 500, 1000]:
        w = hbm_rubin + cpu_je_gpu + x
        print(f"   {cpu_je_gpu:5.0f}                | {x:5.0f}                   | {w:6,.0f} | {w / b300 - 1:+5.0%}   | {(cpu_je_gpu + x) / w:5.0%}")
print()
print("375 = Vera mit halbem SOCAMM bei 1:2, 750 = Vera 1,5 TB bei 1:2, 1500 = Vera 1,5 TB bei 1:1.")
print("X ist frei gesetzt, nicht gemessen: Spannweite, keine Schaetzung.")
print()
for cpu_je_gpu in [375, 750, 1500]:
    x_gleich = hbm_rubin - cpu_je_gpu
    if x_gleich > 0:
        print(f"Bei {cpu_je_gpu:.0f} GB CPU-DRAM je GPU zieht konventionelles DRAM mit HBM gleich ab X = {x_gleich:.0f} GB je GPU.")
    else:
        print(f"Bei {cpu_je_gpu:.0f} GB CPU-DRAM je GPU liegt konventionelles DRAM schon ohne Agenten-Server vor HBM.")
print()
print("Lesart: Welche Zeile gilt, entscheiden zwei Zahlen: ausgelieferte Vera-Konfiguration und")
print("CPU-Server-Stueckzahlen fuer Agenten je installierter GPU.")
