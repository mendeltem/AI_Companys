# P5 SK hynix Q3 2026 gegen den Originalbericht

Stand 2026-11-27 · Status: **erledigt, gegen den Quartalsbericht bestätigt** · Rechnung: [ergebnisse/05](../ergebnisse/05_skhynix_q3_bruecke.txt)

## Ergebnis 2026-11-27

Gewinn- und Verlustrechnung im Quartalsbericht Q3 2026 bei DART (eingereicht 16.11.2026, rcpNo 20261116001715, Tier 1a), Mio KRW, Juli bis September: Umsatz 104.615.483, operatives Ergebnis 83.333.818, Finanzerträge −20.429.273, Finanzaufwand 12.170.116, Ergebnis vor Steuern 50.708.500, Steuern 10.932.907, Nettogewinn 39.775.593, Gewinn je Aktie 54.773 Won (verwässert 54.454). Die Handzeile stimmt auf die Million Won. Offen bleibt nur die Aktienzahl: Die Marktkapitalisierung der Seite rechnet mit 709,85 Mio (yfinance), umlaufend sind nach der Einziehung vom 05.11. rund 705,2 Mio.

## Ergebnis der inneren Prüfung

Die Handzeile in `quartale_hand.json` geht auf: operatives Ergebnis 83,33 − nicht-operativ 32,63 − Steuern 10,93 = 39,77 Bio KRW. Das trifft den gemeldeten Nettogewinn bis auf 1 Mio USD. Die Chat-Werte in USD (77,5 / 61,7 / 29,5, Q1 und Q2) stimmen mit der Seite überein, umgerechnet zu 1.350.

Drei Punkte aus der Brücke, die im Chat fehlen:

1. **Nicht-operativer Rest +1,92 Bio KRW (+1,4 Mrd USD).** Währung −11,63 plus Beteiligungen −22,92 ergeben −34,55, gemeldet sind −32,63. Der Rest ist vermutlich Zinsertrag.
2. **Bereinigter Nettogewinn 47,2 bis 49,5 Mrd USD**, nicht „ca. 48 als obere Grenze“. Mit dem Zinsrest und 21,6 % Steuern sind es 49,5. Mit der Q2-Quote von 23,5 % auf das operative Ergebnis allein sind es 47,2. Offen ist, ob die Bewertungsverluste steuerlich abziehbar sind. Wenn nicht, war die Quote auf das Kerngeschäft niedriger und der bereinigte Gewinn höher. 60 Mrd USD netto bräuchten eine Steuerquote von 2,8 bis 5,0 %, das geht nicht auf.
3. **Aktienzahl.** Nettogewinn / EPS ergibt 726 Mio Aktien, die Seite rechnet mit 709,85 Mio (yfinance). Mit 726 Mio läge die Marktkapitalisierung 2,3 % höher, bei rund 590 statt 577 Mrd USD.

KGV bei 577 Mrd USD: gemeldet Q3 × 4 4,90; bereinigt Q3 × 4 2,98; gemeldet vier Quartale 4,12; operativ Q3 × 4 2,34.

## Gegen den Bericht prüfen

Die Pressemitteilung (`news.skhynix.com/en/q3-2026-business-results/`) ist in dieser Umgebung gesperrt: Die Netzregel lässt den Host nicht zu. Abzugleichen sind diese Posten, in Bio KRW:

| Posten | Handzeile |
|---|---|
| Umsatz | 104,6155 |
| Operatives Ergebnis | 83,3338 |
| Nicht-operatives Ergebnis | −32,63 |
| davon Währung | −11,63 |
| davon Bewertung Beteiligungen | −22,92 |
| Steuern | 10,93 |
| Nettogewinn | 39,7756 |
| EPS (Basis, KRW) | 54.773 |
| Bruttomarge | 86 % (aus der Präsentation, Betrag gerechnet) |

Zusätzlich aus dem Bericht oder Call: gewichtete Aktienzahl, Steueraufwand laut Abschluss, Zinsertrag, HBM-Anteil am DRAM-Umsatz, HBM4-Anteil (für [p2](p2_stueckanteile_hbm4_hbm3e.md)).

## Abschluss

Erledigt, wenn jede Zeile der Tabelle gegen die Pressemitteilung oder Präsentation (Tier 1a) bestätigt oder berichtigt ist. Danach in `daten/skhynix_q3_2026_bruecke.csv` und `quartale_hand.json` den Prüfstatus setzen.
