# AI_Companys

Bewertung und Quartalszahlen von 17 börsennotierten Firmen entlang Nvidias
Lieferkette und Kundschaft. Eine einzelne HTML-Datei, kein Server, kein Build,
keine Abhängigkeiten. Dreisprachig: Deutsch, English, Монгол.

**➜ [Zur interaktiven Seite](https://mendeltem.github.io/AI_Companys/nvidia-oekosystem.html)**



Stand der Daten: 31. Juli 2026. 293 Quartale von 2021-06 bis 2026-06,
12.336 Tagesschlusskurse über drei Jahre.

---

## Link aktivieren

Der Link oben funktioniert erst, wenn GitHub Pages eingeschaltet ist. GitHub
liefert `.html` sonst als Quelltext aus statt sie zu rendern.

1. **Settings → Pages**
2. Unter *Source*: `Deploy from a branch`
3. Branch `main`, Ordner `/ (root)`, **Save**

Nach ein bis zwei Minuten ist die Seite erreichbar. Damit die Adresse kurz
bleibt, die Datei in `index.html` umbenennen; dann genügt
`https://mendeltem.github.io/AI_Companys/`. Ohne Umbenennung lautet der Link
`https://mendeltem.github.io/AI_Companys/nvidia-oekosystem.html`.

Ohne Pages geht es auch direkt, ohne etwas umzustellen:

    https://raw.githack.com/mendeltem/AI_Companys/main/nvidia-oekosystem.html

Oder schlicht herunterladen und doppelklicken. Die Datei enthält alle Daten.

---

## Was drin ist

**Übersicht.** Eine Bewertungskarte, in der jede Kachel eine Firma ist, die
Farbe ihre Bewertungsklasse und der Streifen darunter die
Marktkapitalisierung. Dazu eine sortierbare Vergleichstabelle, ein Streudiagramm
Bewertung gegen Wachstum und ein indexierter Kursvergleich.

**Je Firma eine Unterseite** mit Kurs über drei Jahre, dem Verlauf des
Quartals-KGV, operativem Ergebnis je Quartal, der Differenz zwischen Netto- und
Betriebsergebnis, Umsatz mit operativer Marge, Segmentaufteilung und einer
Tabelle aller Quartale mit Quellenangabe je Zeile.

### Zwei Bewertungsmaße

| Maß | Rechnung | wofür |
|---|---|---|
| KGV (4 Quartale) | Kurs geteilt durch die Summe der letzten vier Quartalsgewinne | der übliche Blick zurück |
| KGV Q×4 | Kurs geteilt durch das jüngste Quartalsergebnis mal vier | bei schnellem Wachstum aussagekräftiger |

Bei stark wachsenden Firmen klaffen beide weit auseinander: Nvidia 29,9 gegen
20,4, Micron 19,8 gegen 8,9, SK hynix 7,5 gegen 3,2. Wo ein Sondereffekt die
Jahressumme unbrauchbar macht, rettet das zweite Maß die Aussage. Sony hat wegen
der Abspaltung des Finanzgeschäfts ein Verlustquartal in der Vierquartalssumme;
das erste Maß ist dort leer, das zweite liefert 68,2.

---

## Firmenkreis

| Ticker | Firma | Rolle gegenüber Nvidia | Handelssymbol | Quartale | Segmente |
|---|---|---|---|---|---|
| NVDA | NVIDIA | Zentrum | NVDA | 20 | 20 |
| TSM | TSMC | Fertiger (Foundry, CoWoS) | 2330.TW | 8 | 4 |
| SKHYNIX | SK hynix | HBM-Hauptlieferant | 000660.KS | 17 | 3 |
| SAMSUNG | Samsung Electronics | HBM-Lieferant, Foundry | 005930.KS | 17 | 0 |
| MU | Micron | HBM-Lieferant | MU | 20 | 12 |
| ARM | Arm Holdings | CPU-IP (Grace, Vera) | ARM | 16 | 9 |
| AVGO | Broadcom | Custom-ASIC, Netzwerk | AVGO | 20 | 7 |
| AMD | AMD | GPU-Wettbewerber | AMD | 20 | 5 |
| DELL | Dell Technologies | Server-OEM | DELL | 20 | 5 |
| MSFT | Microsoft | Kunde (Hyperscaler) | MSFT | 20 | 20 |
| GOOGL | Alphabet | Kunde, zugleich eigener TPU | GOOGL | 20 | 7 |
| AMZN | Amazon | Kunde, zugleich eigener Trainium | AMZN | 20 | 10 |
| META | Meta Platforms | Kunde (Hyperscaler) | META | 21 | 6 |
| ORCL | Oracle | Kunde (OCI) | ORCL | 20 | 16 |
| CRWV | CoreWeave | Kunde (GPU-Neocloud) | CRWV | 9 | 2 |
| SONY | Sony Group | Sensoren, PlayStation | 6758.T | 5 | 0 |
| AAPL | Apple | Endgeräte, Nachfrageseite | AAPL | 20 | 10 |

---

## Datenquellen

**Kurse** aus yfinance, Tagesschlusskurse, jeweils von der Heimatbörse.

**Quartalszahlen** aus SEC-XBRL (`data.sec.gov`, direkt aus den Einreichungen),
yfinance und den Original-Pressemitteilungen beziehungsweise
Ergebnispräsentationen von TSMC, Samsung und SK hynix. Die Quelle steht in jeder
Quartalszeile.

**Segmente** aus den XBRL-Instanzen der einzelnen Einreichungen. Die
Companyfacts-Schnittstelle liefert sie nicht, sie kennt nur Konzernwerte.

---

## Fallstricke, über die dieses Projekt gestolpert ist

Wer so etwas nachbaut, läuft in dieselben. Alle sind im Code kommentiert.

**ADR gegen Heimatbörse.** TSMC und Sony notieren in den USA als ADR in USD, ihre
Gewinne stehen aber in TWD und JPY. Ein KGV aus beidem ergibt für TSMC 3 statt
28. Deshalb laufen beide über 2330.TW und 6758.T.

**Vierte Quartale.** Sie stehen nicht separat im XBRL und müssen als
Geschäftsjahr minus Neunmonatszeitraum rekonstruiert werden. Für Umsatz und
Gewinn ist das exakt. Für gewichtete Aktienzahlen ist es sinnlos: Amazon kam so
auf 12 Millionen statt 10,9 Milliarden Aktien.

**Klammern sind Minuszeichen.** SK hynix schreibt Verluste als `(2,185)`. Wer
die Klammern nur entfernt, macht aus zwei Verlustquartalen der Speicherkrise
Gewinne.

**Broadcom bucht anders.** Der Nettogewinn liegt unter `ProfitLoss`, nicht unter
`NetIncomeLoss`; letzteres endet dort 2019.

**Überlappende Segmentachsen.** Nvidias Produktachse summiert sich auf 192
Prozent des Umsatzes, weil "Data Center" und die Kundenaufteilung
Hyperscale/AI Clouds/Edge nebeneinander in derselben Achse stehen. Gelöst über
eine vollständige Teilmengensuche nach der Kombination, die den Gesamtumsatz
trifft.

**Zweidimensionale Kontexte.** Dell hängt Sparte und `ConsolidationItemsAxis` an
denselben Wert. Wer nur eindimensionale Kontexte nimmt, übersieht Dells Sparten
vollständig.

---

## Bekannte Grenzen

**Nettogewinn je Segment gibt es nicht.** Über acht Firmen geprüft: Umsatz und
operatives Ergebnis tragen eine Segmentdimension, Nettogewinn, Steuern und
Zinsen bei keiner einzigen. Der Standard verlangt nur die Größe, die die
Konzernleitung je Segment tatsächlich steuert. Zinsen, Steuern und
Beteiligungsergebnisse liegen auf Konzernebene. Das Prüfskript liegt bei.

**Samsungs Segmente fehlen.** Die Segmenttabelle liegt in den Präsentationen als
Grafik vor; die Textebene lässt sich nicht verlässlich den Zeilen zuordnen.
Statt womöglich falscher Zahlen steht dort ein Hinweis. Ausgerechnet bei
Samsung wäre die Aufteilung besonders interessant, weil der Konzernumsatz das
Speichergeschäft hinter Handys versteckt.

**Sony hat nur fünf Quartale**, weil dort kein Quartals-XBRL bei der SEC
eingereicht wird. **CoreWeave hat neun**, der Börsengang war im März 2025.

**Währungen.** KGV, Margen und Wachstumsraten sind Verhältniszahlen und damit
währungsunabhängig vergleichbar. Marktkapitalisierung und Umsatz werden für den
Vergleich zu Tageskursen in USD umgerechnet.

Keine Anlageberatung. Zahlen können Extraktionsfehler enthalten; die
Filing-Quelle steht in jeder Quartalszeile.

---

## Zweiter Bericht: KI-Chips 2026

`ki-chips-2026.html` — Lagebericht zu KI-Beschleunigern, Technik und
Marktökonomie. Ergänzt die Bewertungsseite um die andere Hälfte der Frage: was
die 66 Firmen dort eigentlich bauen, und an welcher Stufe der Kette es klemmt.
Wieder eine einzelne HTML-Datei, kein Server, kein Build.

**➜ [Zum Bericht](https://mendeltem.github.io/AI_Companys/ki-chips-2026.html)**

Ohne GitHub Pages, ohne etwas umzustellen:

    https://raw.githack.com/mendeltem/AI_Companys/main/ki-chips-2026.html

Stand der Recherche: 2. September 2026.

### Was drin steht

| Teil | Inhalt |
|---|---|
| Technik | Rack statt Chip (Vera Rubin NVL72), Präzisionsformate FP8/FP4, HBM4, Interconnect, Packaging; Generationsvergleich Rubin, MI450, TPU v7, Trainium, MTIA, Maia, Ascend |
| Engpasskette | Logik-Wafer → HBM → CoWoS → Optik → Netzanschluss, je Stufe mit Status. Der Engpass liegt nicht mehr in der Logikfertigung |
| Markt | 725 Mrd. $ Hyperscaler-Capex 2026, Nvidia Q2 FY27, Marktanteile bei DC-GPUs, Broadcoms Rolle im ASIC-Geschäft |
| Zweite Ordnung | DRAM-Preise, Smartphone- und PC-Prognosen, China-Bifurkation, Abschreibungs- und Stromdebatte |

**Belastbarkeit.** Primärquellen (Nvidia-Quartalsbericht, Deloitte-Ausblick,
UALink-Spezifikation) sind solide. Marktanteile, CoWoS-Kapazitäten,
Huawei-Stückzahlen und alle Capex-Summen sind Analysten- und
Marktforschungsschätzungen mit erheblicher Streuung zwischen Anbietern:
Größenordnungen tragen, Nachkommastellen nicht. Leistungsangaben zu noch nicht
breit ausgelieferten Produkten (Rubin Ultra, MI450, Trainium4) sind
Herstellerangaben unter eigenen Messbedingungen.

### Quellen

**Primär**

- [Nvidia — Q2 FY2027 Financial Results](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)
- [Nvidia — Q1 FY2027 Financial Results](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2027)
- [Deloitte — 2026 Semiconductor Industry Outlook](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-telecom-outlooks/semiconductor-industry-outlook.html)

**Technik und Architekturen**

- [TechPowerUp — Rubin-Architektur im Detail](https://www.techpowerup.com/350947/nvidia-details-the-rubin-architecture-die-annotation-vera-cpu-hbm4-and-disaggregated-inference)
- [VideoCardz — Vera Rubin NVL72](https://videocardz.com/newz/nvidia-vera-rubin-nvl72-detailed-72-gpus-36-cpus-260-tb-s-scale-up-bandwidth)
- [Wikipedia — Rubin (Mikroarchitektur)](https://en.wikipedia.org/wiki/Rubin_(microarchitecture))
- [CNBC — AMD Helios, Microsoft als Erstkunde](https://www.cnbc.com/2026/07/20/amd-helios-microsoft-ai-nvidia.html)
- [Tom's Hardware — Custom AI ASICs, Mai 2026](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia)
- [Spheron — Hyperscaler Custom Chips 2026](https://www.spheron.network/blog/hyperscaler-custom-ai-chips-2026-trainium-tpu-maia-mtia-vs-nvidia-gpu/)
- [Radiant — Co-Packaged Optics mit Vera Rubin Ultra](https://radiant.co/blog/nvidia-vera-rubin-ultra-ushers-in-the-cpo-era)
- [TrendForce — The Inference Economy Arrives](https://insights.trendforce.com/p/ai-inference-chip-architecture)
- [SDxCentral — Cerebras, Groq, Nvidia](https://www.sdxcentral.com/analysis/cerebras-spins-nvidias-groq-tieup-as-proof-its-waferscale-bet-was-right/)
- [Next Waves Insight — On-Device-AI und NPUs](https://nextwavesinsight.com/on-device-ai-2026-apple-pixel-galaxy-npu/)

**Markt, Capex und Lieferkette**

- [Tom's Hardware — Big Tech Capex 725 Mrd. $](https://www.tomshardware.com/tech-industry/big-tech/big-techs-ai-spending-plans-reach-725-billion)
- [Futurum Group — AI Capex 2026](https://futurumgroup.com/insights/ai-capex-2026-the-690b-infrastructure-sprint/)
- [TrendForce — CoWoS-Angebotslücke 20 % auf 10 %](https://www.trendforce.com/news/2026/06/15/news-tsmc-cowos-supply-demand-gap-reportedly-seen-narrowing-from-20-to-10-by-end-2026-as-capacity-expands/)
- [Silicon Analysts — Foundry-Allokation Q1 2026](https://siliconanalysts.com/analysis/foundry-allocation-status-q1-2026)
- [Global Data Center Hub — Microsoft-Capex und Strom-Backlog](https://www.globaldatacenterhub.com/p/microsoft-q3-fy2026-the-190b-capex)

**Speicher und Zweitrundeneffekte**

- [CNBC — KI-Speicher ausverkauft](https://www.cnbc.com/2026/01/10/micron-ai-memory-shortage-hbm-nvidia-samsung.html)
- [IDC — Speicherknappheit, Smartphone- und PC-Markt](https://www.idc.com/resource-center/blog/global-memory-shortage-crisis-market-analysis-and-the-potential-impact-on-the-smartphone-and-pc-markets-in-2026/)
- [Tom's Hardware — Speicherpreise bis Q3 2026](https://www.tomshardware.com/pc-components/ram/memory-price-surge-begins-to-cool-as-consumers-hit-affordability-limit-ai-demand-still-keeps-dram-and-nand-prices-climbing-through-q3-2026)

**China**

- [The Substrate — Chinas KI-Chip-Lieferkette 2026](https://www.the-substrate.net/p/where-chinas-ai-chip-supply-chain)
- [Value Add VC — Exportkontrollen und Huaweis Anteil](https://valueaddvc.com/blog/how-export-controls-on-ai-chips-are-reshaping-global-tech-competition)

Keine Anlageberatung. Marktzahlen sind Schätzungen Dritter.

---

<a name="english"></a>

## English

Valuation and quarterly results for 17 listed companies along Nvidia's supply
chain and customer base. A single HTML file, no server, no build step, no
dependencies. Available in German, English and Mongolian via the switch at the
top left.

**➜ [Open the interactive page](https://mendeltem.github.io/AI_Companys/)**

Data as of 31 July 2026: 293 quarters from 2021-06 to 2026-06, plus 12,336 daily
closing prices across three years.

Prices come from yfinance, taken from each company's home exchange rather than
its ADR, so that price and earnings per share share a currency. Quarterly
figures come from SEC XBRL, from yfinance, and from the original press releases
and earnings presentations of TSMC, Samsung and SK hynix; the source is named in
every quarterly row. Segment figures are pulled from the XBRL instances of
individual filings, because the companyfacts API only exposes consolidated
values.

Two valuation measures sit side by side: the trailing four-quarter P/E, and the
latest quarter's earnings times four. For fast-growing companies the two diverge
sharply, and where a one-off distorts the annual sum, the second measure is the
one that still says something.

Net profit by segment is not shown because it does not exist in the filings.
Checked across eight companies: revenue and operating profit carry a segment
dimension, net profit, tax and interest carry none. Accounting standards only
require the measure management actually steers per segment, which is operating
profit.

Not investment advice. Figures may contain extraction errors.

### AI chips report

`ki-chips-2026.html` — a companion report on AI accelerators: what these
companies actually build, and where the chain binds. Architectures from rack to
memory, the bottleneck chain from logic wafers through HBM, CoWoS and optics to
grid power, and the market economics around it. As of 2 September 2026.

**➜ [Open the report](https://mendeltem.github.io/AI_Companys/ki-chips-2026.html)**

Market shares, packaging capacities and capex totals are third-party estimates;
orders of magnitude hold, decimal places do not.
