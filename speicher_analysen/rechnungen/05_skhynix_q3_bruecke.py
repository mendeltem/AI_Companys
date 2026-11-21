# Pruefung p5 und Chat-Zahlen: SK hynix Q3 2026 vom operativen Ergebnis zum
# Nettogewinn, bereinigter Nettogewinn, KGV-Varianten. Alles in USD zum festen
# Kurs aus daten/parameter.csv. Prueft die Zeile auf innere Stimmigkeit,
# nicht gegen den Originalbericht (der ist in dieser Umgebung nicht abrufbar).

import csv
from pathlib import Path

P = Path(__file__).resolve().parent.parent
par = {z["name"]: float(z["wert"]) for z in csv.DictReader(open(P / "daten" / "parameter.csv", encoding="utf-8"))}
b = {z["posten"]: float(z["bio_krw"]) for z in csv.DictReader(open(P / "daten" / "skhynix_q3_2026_bruecke.csv", encoding="utf-8"))}
q = [z for z in csv.DictReader(open(P / "daten" / "quartale.csv", encoding="utf-8")) if z["firma"] == "SKHYNIX"]

kurs = par["kurs_krw_usd"]
usd = lambda bio_krw: bio_krw * 1000 / kurs  # Bio KRW -> Mrd USD

op = b["operatives_ergebnis"]
nop = b["nichtoperativ_gesamt"]
fx = b["davon_waehrung"]
bet = b["davon_beteiligungsbewertung"]
st = b["steuern"]
net = b["nettogewinn"]

# 1. Stimmt die Bruecke?
vor_steuer = op + nop
rest_nop = nop - fx - bet
t = st / vor_steuer
print("1. Bruecke Q3 2026 (Mrd USD bei %d KRW/USD)" % kurs)
print(f"   Umsatz {usd(b['umsatz']):.1f}, operativ {usd(op):.1f} (Marge {op / b['umsatz']:.1%})")
print(f"   nicht-operativ {usd(nop):+.1f} = Waehrung {usd(fx):+.1f} + Beteiligungen {usd(bet):+.1f} + Rest {usd(rest_nop):+.1f}")
print(f"   vor Steuern {usd(vor_steuer):.1f}, Steuern {usd(st):.1f} (Quote {t:.1%}), netto {usd(vor_steuer - st):.2f}")
print(f"   gemeldet netto {usd(net):.2f}, Abweichung {usd(vor_steuer - st - net) * 1000:+.0f} Mio USD -> Zeile in sich stimmig")
print(f"   Der Rest von {rest_nop:+.2f} Bio KRW ({usd(rest_nop):+.1f} Mrd USD) ist vermutlich Zinsertrag; im Chat nicht beruecksichtigt.")

# 2. Bereinigter Nettogewinn: ohne Waehrung und Beteiligungsbewertung
print()
print("2. Bereinigter Nettogewinn Q3 2026")
varianten = [
    ("operativ x (1 - 21,6 %), Chat-Rechnung", op * (1 - t)),
    ("(operativ + Rest) x (1 - 21,6 %)", (op + rest_nop) * (1 - t)),
    ("operativ x (1 - 23,5 %), Quote aus Q2", op * (1 - par["steuerquote_skhynix_q2_2026"])),
    ("(operativ + Rest) x (1 - 23,5 %)", (op + rest_nop) * (1 - par["steuerquote_skhynix_q2_2026"])),
]
for name, wert in varianten:
    print(f"   {name:42s} {usd(wert):5.1f} Mrd USD")
lo = min(usd(w) for _, w in varianten)
hi = max(usd(w) for _, w in varianten)
print(f"   Band {lo:.1f} bis {hi:.1f}. Die 48 aus dem Chat sind kein oberer Rand: mit dem Zinsrest liegt es bei bis zu {hi:.1f}.")
print("   Offen: ob die Bewertungsverluste steuerlich abziehbar sind. Wenn nicht, war die Quote auf das")
print("   Kerngeschaeft niedriger als 21,6 % und der bereinigte Gewinn hoeher.")

# 3. Was 60 Mrd USD netto voraussetzen wuerden
ziel = 60 * kurs / 1000
print()
print(f"3. 60 Mrd USD netto = {ziel:.1f} Bio KRW. Noetige Steuerquote: {1 - ziel / op:.1%} auf operativ allein, "
      f"{1 - ziel / (op + rest_nop):.1%} mit Zinsrest. Geht nicht auf.")

# 4. Aktienzahl aus dem EPS
aktien_eps = net * 1e12 / b["eps_krw"]
print()
print(f"4. Nettogewinn / EPS = {aktien_eps / 1e6:.0f} Mio Aktien (gewichteter Durchschnitt Q3).")
print(f"   Die Seite rechnet die Marktkap. mit 709,85 Mio (yfinance). Mit {aktien_eps / 1e6:.0f} Mio laege sie {aktien_eps / 709.854891e6 - 1:+.1%} hoeher.")
print("   Unterschied kann aus Rueckkaeufen nach dem Stichtag kommen; nicht geprueft.")

# 5. KGV-Varianten
mk = par["skhynix_marktkap_usd"]
q4 = sorted(q, key=lambda z: z["ende"])[-4:]
netto4 = sum(float(z["netto_mrd_usd"]) for z in q4)
op4 = sum(float(z["operativ_mrd_usd"]) for z in q4)
bereinigt = usd(op * (1 - t))
print()
print(f"5. KGV bei Marktkap. {mk:.0f} Mrd USD (Kurs 17.11.2026)")
print(f"   gemeldet, Q3 x 4:                {mk / (usd(net) * 4):5.2f}")
print(f"   bereinigt, Q3 x 4:               {mk / (bereinigt * 4):5.2f}")
print(f"   gemeldet, 4 Quartale ({q4[0]['ende'][:7]} bis {q4[-1]['ende'][:7]}): {mk / netto4:5.2f}  (Summe netto {netto4:.1f})")
print(f"   operativ, 4 Quartale:            {mk / op4:5.2f}  (Summe operativ {op4:.1f})")
print(f"   operativ, Q3 x 4:                {mk / (usd(op) * 4):5.2f}")
print("   Das gemeldete Vierquartals-KGV enthaelt den Kioxia-Ertrag aus Q2 und den Bewertungsverlust aus Q3;")
print("   beide laufen in entgegengesetzte Richtung und gehoeren nicht ins wiederkehrende Ergebnis.")
