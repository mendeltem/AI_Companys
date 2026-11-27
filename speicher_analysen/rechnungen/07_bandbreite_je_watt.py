# These 4: Mehr Bandbreite -> mehr Tokens pro Watt -> Aufruestzwang.
#
# Frage: Welcher Teil des Leistungsgewinns je MW von Blackwell (B300) auf
# Rubin laesst sich aus der Speicherbandbreite je Watt erklaeren?
# Ist die Decode-Phase bandbreitengebunden, skaliert Tokens/s je GPU mit der
# Bandbreite, Tokens je Watt also mit Bandbreite je Watt. Anteil am Gewinn
# auf log-Skala: ln(Bandbreitenfaktor je W) / ln(Gesamtfaktor je MW).

import csv
import math
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}

bw_alt = par["bandbreite_b300"] / par["tdp_b300"] * 1000   # TB/s je kW
print(f"B300: {par['bandbreite_b300']:.1f} TB/s bei {par['tdp_b300']:.0f} W = {bw_alt:.2f} TB/s je kW")
for name in ["bandbreite_rubin_alt", "bandbreite_rubin_neu"]:
    bw_neu = par[name] / par["tdp_rubin"] * 1000
    f_bw = bw_neu / bw_alt
    print(f"Rubin {par[name]:.1f} TB/s bei {par['tdp_rubin']:.0f} W = {bw_neu:.2f} TB/s je kW, Faktor {f_bw:.2f}")
    for quelle in ["leistung_je_mw_semianalysis", "leistung_je_mw_nvidia"]:
        f = par[quelle]
        print(f"   gegen {f:.1f}x je MW ({quelle.split('_')[-1]}): Bandbreite erklaert {math.log(f_bw) / math.log(f):.0%} (log), "
              f"Rest Faktor {f / f_bw:.2f} aus Rechenformat, NVLink, Batching, Software")

print()
gb_mw_alt = par["hbm_gb_b300"] / par["tdp_b300"] * 1e6
gb_mw_neu = par["hbm_gb_rubin"] / par["tdp_rubin"] * 1e6
print(f"HBM-Kapazitaet je MW: B300 {gb_mw_alt:,.0f} GB, Rubin {gb_mw_neu:,.0f} GB ({gb_mw_neu / gb_mw_alt - 1:+.0%})")
waf_alt = gb_mw_alt * par["tausch_hbm3e"]
waf_neu = gb_mw_neu * par["tausch_hbm4"]
print(f"HBM-Waferaequivalent je MW (x Tauschverhaeltnis): B300 {waf_alt:,.0f}, Rubin {waf_neu:,.0f} ({waf_neu / waf_alt - 1:+.1%})")
print("   -> Tausch bei festem Strom ist fuer HBM-Wafer nahezu neutral: weniger GB, aber teurere GB.")
print()
print("Lesart: Die Bandbreite je Watt steigt um den Faktor 1,9 bis 2,1. Das erklaert 27 bis 45 % des")
print("Gewinns je MW (log), je nach Bandbreitenwert und Quelle des Gesamtfaktors. Die Richtung der These")
print("traegt, der groessere Teil des Gewinns kommt aber nicht aus dem Speicher. Fuer den Speichermarkt")
print("zaehlt zudem: je MW verbaut Rubin")
print("weniger HBM-Kapazitaet als B300. Aufruesten bei festem Strom kauft also mehr Bandbreite,")
print("nicht mehr Bits je MW. Mehr Bits kommen erst ueber mehr MW oder mehr GB je GPU (Rubin Ultra).")
print()
print("Aufruestschwelle (nicht gerechnet, Eingaben fehlen mit Quelle):")
print("  Tausch lohnt, wenn (f - 1) x Erloes je MW-Jahr x Restjahre > Capex neu je MW - Restwert alt je MW.")
print("  Benoetigt: Rack-Preis Rubin je MW, Erloes je MW-Jahr (Tokenpreis), Restwert Blackwell (Gebrauchtmarkt).")
