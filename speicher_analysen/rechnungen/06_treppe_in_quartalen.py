# Pruefung p3 und These 1: Zeigt Nvidia seit 2023 eine Treppe?
#
# Messgroesse: Zuwachs in Mrd USD je Quartal, d_t = U_t - U_(t-1).
# Treppe in den Zuwaechsen heisst:
#   innerhalb einer Generation bleibt d_t ungefaehr flach (Stufe),
#   beim Wechsel faellt d_t kurz (Uebergang), danach liegt es ueber der alten Stufe
#   und faellt nicht auf sie zurueck.
# Welle heisst: nach dem Hoch faellt d_t auf oder unter die alte Stufe.
#
# Nebenbefund, rein arithmetisch: Bei flachem d_t faellt die Wachstumsrate in
# Prozent von selbst. "Wachstum verlangsamt sich" in Prozent ist bei einer
# flachen Stufe kein Signal.
#
# Quartale mit 14 Wochen (aus den Stichtagen: mehr als 95 Tage) werden
# zusaetzlich auf 13 Wochen umgerechnet, sonst steckt eine Woche im Zuwachs.
#
# Generationen nur zur Lesehilfe, nicht aus den Zahlen abgeleitet:
#   Hopper-Hochlauf ab Quartal bis Jul 2023 (allgemein bekannt, ohne Quelle hier)
#   GB300-Hochlauf Aug bis Okt 2025 (Wiki gb300-ramp-timing-and-rubin-handover, Tier 1a)
#   Rubin-Auslieferung ab Aug 2026 (Wiki rubin-shipments-start-q3-fy27)

import csv
import datetime as dt
from pathlib import Path

P = Path(__file__).resolve().parent.parent
q = list(csv.DictReader(open(P / "daten" / "quartale.csv", encoding="utf-8")))

def reihe(firma, ab):
    z = sorted([r for r in q if r["firma"] == firma and r["umsatz_mrd_usd"] != ""], key=lambda r: r["ende"])
    return [(r["ende"], float(r["umsatz_mrd_usd"])) for r in z if r["ende"] >= ab]

def zeige(firma, ab):
    r = reihe(firma, ab)
    print(f"{firma}: Quartalsende | Umsatz Mrd USD | Zuwachs Mrd | Zuwachs % | Tage")
    for i in range(1, len(r)):
        tage = (dt.date.fromisoformat(r[i][0]) - dt.date.fromisoformat(r[i - 1][0])).days
        d = r[i][1] - r[i - 1][1]
        zeile = f"  {r[i][0]} | {r[i][1]:7.1f} | {d:+6.1f} | {d / r[i - 1][1]:+6.1%} | {tage}"
        if tage > 95:
            u13 = r[i][1] * 13 / 14
            zeile += f"  14 Wochen; auf 13 Wochen {u13:.1f}, Zuwachs {u13 - r[i - 1][1]:+.1f} ({u13 / r[i - 1][1] - 1:+.1%})"
        print(zeile)
    return r

nv = zeige("NVDA", "2022-10-01")
u = dict(nv)

# Stufen: Mittel der Zuwaechse je Abschnitt
def stufe(r, von, bis):
    d = [r[i][1] - r[i - 1][1] for i in range(1, len(r)) if von <= r[i][0] <= bis]
    return sum(d) / len(d), len(d)

s1, n1 = stufe(nv, "2023-10-01", "2025-05-01")
s2, n2 = stufe(nv, "2025-10-01", "2026-08-01")
print()
print(f"Stufe Hopper/fruehes Blackwell (Okt 2023 bis Apr 2025, {n1} Quartale): {s1:.1f} Mrd je Quartal")
print(f"Uebergang Jul 2025: {u['2025-07-27'] - u['2025-04-27']:+.1f}")
print(f"Stufe GB300 (Okt 2025 bis Jul 2026, {n2} Quartale): {s2:.1f} Mrd je Quartal")
print(f"Okt 2026 (Rubin beginnt): {u['2026-10-25'] - u['2026-07-26']:+.1f}")

# Ausblick Q4 GJ2027: 130 Mrd fuer 14 Wochen (Pressemitteilung 2026-11-17, in der Seite vermerkt)
ausblick = 130.0
auf13 = ausblick * 13 / 14
letzt = u["2026-10-25"]
print(f"Ausblick Jan 2027: {ausblick:.0f} Mrd fuer 14 Wochen, auf 13 Wochen {auf13:.1f}: "
      f"Zuwachs {ausblick - letzt:+.1f} nominal, {auf13 - letzt:+.1f} auf 13 Wochen")
print("Bruchkante: Liegen die Zuwaechse in den Quartalen bis Apr und Jul 2027 unter der GB300-Stufe")
print(f"({s2:.1f} Mrd), ist es bei Nvidia eine Welle, keine Treppe.")

print()
sk = zeige("SKHYNIX", "2024-09-01")
print()
mu = zeige("MU", "2024-08-01")
print()
print("Lesart SK hynix: Zuwaechse Q2 und Q3 2026 fast gleich, die Rate in Prozent faellt trotzdem von 51 auf 32 %.")
print("Das ist die Arithmetik einer flachen Stufe, kein Abschwung.")
print("Lesart Micron: Das Quartal bis 03.09.2026 hat 14 Wochen. Auf 13 Wochen sinkt der Zuwachs deutlich;")
print("die gemeldeten +31 % ueberzeichnen das Quartal um eine Woche.")
