# Speicher-Analysen

Arbeitsordner zu Mendels fünf Thesen über HBM, DRAM und die Treppe der Waferkannibalisierung. Stand 2026-11-21.

Übergabe aus dem claude.ai-Projekt DATACENTER RESEARCH. Grundlage im Wiki ([blackbeard_wikki](https://github.com/mendeltem/blackbeard_wikki), Commit c563194): `knowledge/memory_supply`, `knowledge/ai_demand_drivers`, `knowledge/memory_earnings`.

**Arbeitsteilung mit dem Wiki.** Das Wiki hält das Wissen. Dieser Ordner hält die Rechnungen, die Eingabedaten mit Quelle und den Stand der Prüfungen. Was hier trägt, wandert als Eintrag ins Wiki. Wiki-Inhalte werden verlinkt, nicht kopiert.

## Stand auf einen Blick

| | Frage | Ergebnis bisher | Status |
|---|---|---|---|
| [T1](thesen/t1_treppe_statt_welle.md) | Treppe statt Welle | Schritt 2026 → 2027: 84 % Menge, 16 % Mix. Nvidia-Zuwächse bilden eine Treppe (4,4 → 12,4 → 19,6 Mrd je Quartal) | vorschlag |
| [T2](thesen/t2_engpass_beim_angebot.md) | Engpass beim Angebot | Konv. DRAM verliert Wafer, wenn die Zufuhr 2027 nicht um mehr als 11,4 % wächst; Lage geteilt: Server/HBM angebotsbegrenzt, Konsum preisbegrenzt | vorschlag |
| [T3](thesen/t3_hbm4_vorrang.md) | 2027 mehr HBM4 als HBM3E | Samsungs 60 % Umsatz entsprechen 33 bis 50 % der Bits; Jahresmittel 2027 etwa 55 %, Q4 2027 etwa 80 % | vorschlag |
| [T4](thesen/t4_bandbreite_tokens_je_watt.md) | Bandbreite → Tokens/W → Aufrüsten | Bandbreite je W erklärt 27 bis 45 % des Gewinns je MW; HBM-Wafer je MW bleiben beim Tausch fast gleich (+3,7 %) | vorschlag |
| [T5](thesen/t5_server_dram_agenten.md) | Server-DRAM wegen Agenten | Eine Messgröße reicht für das Rack (CPU-DRAM je GPU), dazu eine zweite für Agenten-Server; Kippwerte gerechnet | vorschlag |
| [P1](pruefungen/p1_tauschverhaeltnis.md) | 2,9:1 gegen 4:1 | Rundung verworfen; Bezugsbasis plausibel; TrendForce' 30 % enthalten wohl keinen HBM4-Aufschlag | offen, eingegrenzt |
| [P2](pruefungen/p2_stueckanteile_hbm4_hbm3e.md) | Stückanteile HBM4/HBM3E | Umrechnung Umsatz → Bits steht, Quelle fehlt | offen |
| [P3](pruefungen/p3_nvidia_treppe.md) | Nvidia-Treppe seit 2023 | beschreibend bestätigt; „angekündigt“ ungeprüft; Bruchkante 12,4 Mrd | teilweise |
| [P4](pruefungen/p4_agenten_server_dram.md) | Agentenanteil Server-DRAM | Messgrößen und Kippwerte festgelegt | offen |
| [P5](pruefungen/p5_skhynix_q3_gegen_bericht.md) | SK hynix Q3 gegen Bericht | in sich stimmig; Bericht hier nicht abrufbar | offen |

## Wo die Rechnung von der Übergabe abweicht

1. **SK hynix bereinigt netto: 47,2 bis 49,5 Mrd USD, nicht „ca. 48 als obere Grenze“.** Im nicht-operativen Ergebnis steckt ein Rest von +1,4 Mrd USD (wohl Zinsen). 60 Mrd bleiben ausgeschlossen. ([05](ergebnisse/05_skhynix_q3_bruecke.txt))
2. **Die Treppe besteht vor allem aus Menge, und Menge kann zurückfallen.** Nur der strukturelle Teil, rund ein Sechstel, rastet ein. ([01](ergebnisse/01_wafer_mix_menge.txt))
3. **TrendForce' 30 % für 2027 enthalten keinen Mix-Aufschlag**, das implizite Verhältnis bleibt bei 2,85/2,87. Mit Aufschlag wären es 31,5 %, und die Schwelle für konventionelles DRAM stiege auf 13,9 %. ([01](ergebnisse/01_wafer_mix_menge.txt), [02](ergebnisse/02_schwelle_standard_dram.txt))
4. **Micron FQ4 2026 hatte 14 Wochen.** Auf 13 Wochen gerechnet sind es +21,5 % statt +30,8 % zum Vorquartal. Den Wiki-Kurzstand memory_earnings betrifft das. ([06](ergebnisse/06_treppe_in_quartalen.txt))
5. **SK hynix Aktienzahl:** Das EPS impliziert 726 Mio Aktien, die Seite rechnet mit 709,85 Mio. Die Marktkapitalisierung läge dann bei rund 590 statt 577 Mrd USD. Nicht geprüft.

Kurz:
- Mix 1,8 (feste Wafer) gegen 1,5 (feste Bitanteile) ist eine Frage der Rahmung, kein Fehler.
- Die Schwelle von 11,4 % bestätigt sich.
- Die Q1- bis Q3-Zeilen in USD stimmen mit der Seite.

## Aufbau

    speicher_analysen/
      README.md                 dieser Überblick
      thesen/                   t1 bis t5: Aussage, Rechnung, trägt / trägt nicht, Bruchindikator, nächste Prüfung
      pruefungen/               p1 bis p5: offene Punkte mit Methode und Abschlusskriterium
      daten/
        parameter.csv           jede Annahme mit Wert, Stand, Quelle, Tier, Link
        quartale.csv            aus der Seite gezogen (Skript 00), mit Quelle und Prüfstatus je Zeile
        skhynix_q3_2026_bruecke.csv
      rechnungen/               00 bis 08, linear, ohne main(), jede Zeile druckbar
      ergebnisse/               Ausgabe jedes Skripts als .txt, mit eingecheckt

| Skript | rechnet |
|---|---|
| 00_quartale_aus_seite | Quartale Nvidia, SK hynix, Samsung, Micron aus `nvidia-oekosystem.html` nach `daten/quartale.csv` |
| 01_wafer_mix_menge | Mix gegen Menge im HBM-Waferanteil, zwei Rahmungen, Shapley-Zerlegung |
| 02_schwelle_standard_dram | Waferschwelle 11,4 % und Bitschwelle 4,6 % für konventionelles DRAM |
| 03_tauschverhaeltnis_implizit | TrendForce-implizites Verhältnis, Rundungsband, nötiger Dichteabstand |
| 04_umsatz_zu_bitanteil | Umsatzanteil HBM4 → Bitanteil je Preisverhältnis, Kipppunkt |
| 05_skhynix_q3_bruecke | operativ → netto, bereinigter Gewinn, KGV-Varianten, Aktienzahl |
| 06_treppe_in_quartalen | Zuwächse je Quartal, Stufen, 14-Wochen-Quartale |
| 07_bandbreite_je_watt | Bandbreite je W gegen Leistung je MW, HBM-GB und Wafer je MW |
| 08_cpu_dram_je_gpu | Waferäquivalent je GPU mit CPU-DRAM und Agenten-Servern |

## Rechnen

Alle Skripte finden ihre Dateien über den eigenen Pfad, das Arbeitsverzeichnis ist egal. Nur Standardbibliothek.

```bash
P=/home/user/AI_Companys/speicher_analysen
for f in $P/rechnungen/*.py; do python3 "$f" > "$P/ergebnisse/$(basename "$f" .py).txt"; done
```

Einzeln:

```bash
python3 /home/user/AI_Companys/speicher_analysen/rechnungen/01_wafer_mix_menge.py
```

Eine Annahme ändern: den Wert in `daten/parameter.csv` ersetzen, Quelle und Tier mitziehen, alles neu laufen lassen. Neue Quartale: zuerst die Seite aktualisieren, dann `00`.

## Quellenstufen

Wie im Wiki (`memory_earnings/data/README.md`):

| Tier | Bedeutung |
|---|---|
| 1a | Einreichungen, Berichte, Investor Relations, Calls |
| 1b | Newsroom und Datenblätter der Firma |
| 2 | Branchendienste (TrendForce) und etablierte Presse |
| 3 | Blogs, Aggregatoren: Spur, kein Befund |
| „1b über 2“ | Firmenaussage, nur über Presse gelesen |
| eigen | eigene Rechnung; trägt nur so weit wie ihre Eingaben |
| offen | Wert aus dem Chat ohne vermerkte Herkunft |

Die eigene Seite ist keine Quelle (Wiki-Regel own-visualisation-is-not-a-source). `quartale.csv` übernimmt deshalb Quelle und Prüfstatus jeder Zeile aus der Seite. Handzeilen gelten bis zur Gegenprüfung als ungeprüft.

## Umrechnung

KRW zu festem Kurs 1.350 je USD (Setzung). Damit bleiben Wachstumsraten in USD dieselben wie in KRW. Die Seite selbst rechnet zum Tageskurs (1.335).

## Ins Wiki zu übertragen

Das muss jemand mit Schreibrecht auf das Wiki eintragen:
- `hbm-generation-change-ratchets-cannibalisation`: Mix 1,5 / Menge 8,0 nach Shapley. TrendForce ohne Mix-Aufschlag. Gegenargument „Menge ist der umkehrbare Teil“.
- `memory_earnings/SUMMARY.md`: Micron FQ4 hatte 14 Wochen, auf 13 Wochen +21,5 %.
- `memory_earnings`: SK hynix Q3 bereinigt 47,2 bis 49,5 Mrd USD, Brücke mit Zinsrest.
- `ai_demand_drivers`: Nvidia-Treppe in den Zuwächsen als Befund, mit Bruchkante 12,4 Mrd.

Keine Anlageberatung.
