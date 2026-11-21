# P3 Nvidia-Treppe seit 2023 an Quartalszahlen

Stand 2026-11-21 · Status: **beschreibend bestätigt, Vorhersage offen** · Rechnung: [ergebnisse/06](../ergebnisse/06_treppe_in_quartalen.txt)

## Ergebnis

Gemessen am Umsatzzuwachs je Quartal (SEC-XBRL, Tier 1a) ergibt sich eine Treppe:

    Stufe 1  Okt 2023 bis Apr 2025   4,4 Mrd USD je Quartal   (Wachstumsrate fällt dabei von 34 auf 12 %)
    Delle    Jul 2025                +2,7
    Stufe 2  Okt 2025 bis Jul 2026   12,4 Mrd USD je Quartal  (Rate um 18 bis 22 %)
    Okt 2026                         +19,6
    Ausblick Jan 2027                +4,9 auf 13 Wochen (+14,2 nominal, das Quartal hat 14 Wochen)

Seit Jan 2023 ist der Umsatz in keinem Quartal gefallen. Fällt die Rate in Prozent innerhalb einer Stufe, ist das Arithmetik: Bei gleichem Zuwachs sinkt die Rate mit wachsender Basis.

Dieselbe Rechnung für die Speicherhersteller:
- SK hynix: Q2 und Q3 2026 je rund 19 Mrd USD Zuwachs. Die Rate fällt trotzdem von 51 auf 32 %.
- Micron: Das Quartal bis 03.09.2026 hat 14 Wochen (aus den Stichtagen, 98 Tage). Auf 13 Wochen gerechnet, steigt der Umsatz um +21,5 % statt um die gemeldeten +30,8 %. Der Wiki-Kurzstand memory_earnings nennt „+31 % Q/Q, Wachstum verlangsamt“. Die Verlangsamung ist damit stärker als gemeldet.

## Was offen ist

1. **„Angekündigt“**: Mendels Beobachtung lautet „Verlangsamung angekündigt, dann neuer Schub“. Prüfen lässt sich das nur mit einer Reihe aus Ausblick gegen Ist je Quartal (Nvidia-Pressemitteilungen, Tier 1a) und gegebenenfalls Pressezitaten. Diese Reihe fehlt noch.
2. **Vorhersage**: Wenn die Treppe hält, folgt auf die Delle im Jan 2027 eine Stufe über 12,4 Mrd USD je Quartal.

## Bruchkante

Liegen die Zuwächse in den Quartalen bis Apr 2027 und bis Jul 2027 beide unter 12,4 Mrd USD, ist es bei Nvidia eine Welle.

## Grenze

Die Nvidia-Reihe misst Umsatz, keine Waferkannibalisierung. Sie ist eine Parallele zu T1, kein Beleg für die Speicherseite.

## Nachtragen

Nach jedem Nvidia-Bericht: Sobald die Seite den neuen Stand trägt (über den täglichen Lauf `werkzeuge/taeglich_seite.py` oder einen Handeintrag in `quartale_hand.json`), hier `00` und `06` neu laufen lassen.
