# AI_Companys

Bewertung und Quartalszahlen von 66 börsennotierten Firmen entlang Nvidias
Lieferkette, Kundschaft und Nachfrageseite. Eine einzelne HTML-Datei, kein
Server, kein Build, keine Abhängigkeiten. Dreisprachig: Deutsch, English,
Монгол.

**➜ [Zur interaktiven Seite](https://mendeltem.github.io/AI_Companys/nvidia-oekosystem.html)**

Stand der Daten: 6. August 2026. 1069 Quartale von 2019-02 bis 2026-07,
47.839 Tagesschlusskurse über drei Jahre. Alle Beträge in US-Dollar.

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

Die Seite verweist auf `manifest.webmanifest`, `favicon-32.png`,
`apple-touch-icon.png` und `sw.js`. Diese Dateien liegen nicht im Repo; die
Verweise laufen ins Leere, in der Konsole stehen 404er, und installieren lässt
sich die Seite nicht. Entweder die vier Dateien ergänzen oder die Verweise im
Kopf der HTML entfernen.

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

Bei stark wachsenden Firmen klaffen beide weit auseinander: Nvidia 33,6 gegen
22,9, Micron 20,2 gegen 9,1, SK hynix 6,6 gegen 2,8. Wo ein Sondereffekt die
Jahressumme unbrauchbar macht, rettet das zweite Maß die Aussage. Sony hat wegen
der Abspaltung des Finanzgeschäfts ein Verlustquartal in der Vierquartalssumme;
das erste Maß ist dort leer, das zweite liefert 15,7.

### Alles in Dollar

Zehn Firmen bilanzieren nicht in Dollar: TSMC, UMC, ASE und Hon Hai in TWD,
SK hynix und Samsung in KRW, Kioxia und Sony in JPY, ams OSRAM in CHF,
RoboSense in HKD. Ihre Kurse, Quartalszahlen und Segmentreihen werden beim Laden
der Seite umgerechnet, Kurs und Gewinn je Aktie mit demselben Faktor. Genau
deshalb bleiben KGV, Kurs-Umsatz-Verhältnis, Margen und Wachstumsraten
unberührt: Zähler und Nenner werden gleich skaliert.

Der Faktor ist fest, vom Datenstand, und nicht historisch je Handelstag. Ein
Tageskurs je Punkt würde die Währungsbewegung in die Kurskurve mischen, und die
Kurve zeigte dann zwei Dinge gleichzeitig. Im Firmenkopf steht weiterhin, in
welcher Währung bilanziert wird. Wer die Heimatwährung sehen will, setzt in der
HTML `const IN_USD = true` auf `false`; die Rohdaten stehen unverändert in der
Datei.

---

## Firmenkreis

66 Firmen, nach Schichten der Kette sortiert wie auf der Seite selbst, innerhalb
der Schicht nach Marktkapitalisierung.

| Ticker | Firma | Rolle | Handelssymbol | Quartale | Segmente |
|---|---|---|---|---|---|
| NVDA | NVIDIA | GPU-Entwurf, Systeme, Software | NVDA | 20 | 20 |
| AVGO | Broadcom | Custom-ASIC, Netzwerkchips | AVGO | 20 | 7 |
| AMD | AMD | GPU- und CPU-Entwurf | AMD | 21 | 5 |
| ARM | Arm Holdings | CPU-Architektur als Lizenz | ARM | 16 | 9 |
| MRVL | Marvell | Custom-Silizium, Optik-DSP | MRVL | 20 | 0 |
| TSM | TSMC | Auftragsfertigung, CoWoS | 2330.TW | 8 | 4 |
| INTC | Intel | Eigene Chips und Auftragsfertigung | INTC | 20 | 0 |
| UMC | UMC | Auftragsfertigung reifer Knoten | 2303.TW | 6 | 0 |
| GFS | GlobalFoundries | Auftragsfertigung Spezialknoten | GFS | 5 | 0 |
| ASML | ASML | Lithografie, EUV-Monopol | ASML | 5 | 0 |
| AMAT | Applied Materials | Beschichtung, Ätzen, Inspektion | AMAT | 20 | 0 |
| LRCX | Lam Research | Ätzen, Abscheidung, HBM-Stapel | LRCX | 21 | 0 |
| KLAC | KLA | Prozesskontrolle, Defektprüfung | KLAC | 21 | 0 |
| MU | Micron | DRAM, HBM, NAND | MU | 20 | 12 |
| SAMSUNG | Samsung Electronics | DRAM, NAND, eigene Fertigung | 005930.KS | 17 | 0 |
| SKHYNIX | SK hynix | HBM-Marktführer, DRAM, NAND | 000660.KS | 17 | 3 |
| SNDK | SanDisk | NAND-Flash | SNDK | 6 | 0 |
| KIOXIA | Kioxia | NAND-Flash | 285A.T | 3 | 0 |
| ASE | ASE Technology | Montage und Test, größter OSAT | 3711.TW | 7 | 0 |
| AMKR | Amkor | Montage und Test | AMKR | 21 | 0 |
| ANET | Arista Networks | Rechenzentrums-Switching | ANET | 21 | 0 |
| COHR | Coherent | Optische Transceiver, Laser | COHR | 20 | 0 |
| ALAB | Astera Labs | Verbindungs-Silizium | ALAB | 20 | 0 |
| CRDO | Credo | Serdes, aktive Kupferkabel | CRDO | 20 | 0 |
| DELL | Dell Technologies | Server, KI-Fabriken | DELL | 20 | 5 |
| HONHAI | Hon Hai (Foxconn) | Auftragsmontage der KI-Racks | 2317.TW | 5 | 0 |
| HPE | Hewlett Packard Enterprise | Server, Netzwerk, KI-Systeme | HPE | 14 | 0 |
| SMCI | Super Micro | Server, Flüssigkühlung | SMCI | 20 | 0 |
| GEV | GE Vernova | Turbinen, Netztechnik | GEV | 14 | 0 |
| VRT | Vertiv | Kühlung, Rack-Stromversorgung | VRT | 20 | 0 |
| MPWR | Monolithic Power | Leistungshalbleiter für Racks | MPWR | 21 | 0 |
| GOOGL | Alphabet | Google Cloud, eigene TPU | GOOGL | 20 | 7 |
| MSFT | Microsoft | Azure, Beteiligung an OpenAI | MSFT | 20 | 20 |
| AMZN | Amazon | AWS, eigenes Trainium | AMZN | 20 | 10 |
| META | Meta Platforms | Eigene Rechenzentren, MTIA | META | 21 | 6 |
| ORCL | Oracle | OCI, Vermietung an KI-Labore | ORCL | 20 | 16 |
| NBIS | Nebius | GPU-Vermietung, Europa | NBIS | 20 | 0 |
| CRWV | CoreWeave | GPU-Vermietung, Neocloud | CRWV | 9 | 2 |
| PLTR | Palantir | Agentenplattform für Behörden, Industrie | PLTR | 21 | 0 |
| CRM | Salesforce | Vertriebssoftware, Agentforce | CRM | 20 | 0 |
| APP | AppLovin | KI-Werbemaschine, Auktionsmodelle | APP | 21 | 0 |
| NOW | ServiceNow | Arbeitsabläufe mit Agenten | NOW | 20 | 0 |
| INTU | Intuit | Steuer- und Buchhaltung mit Agenten | INTU | 20 | 0 |
| DUOL | Duolingo | Sprachkurse, KI-Abostufen | DUOL | 20 | 0 |
| LLY | Eli Lilly | Pharma, kauft Rechenzeit und Modelle | LLY | 21 | 0 |
| TEM | Tempus AI | Klinische Daten und Diagnostik | TEM | 12 | 0 |
| CERT | Certara | Biosimulation für Zulassungsdossiers | CERT | 21 | 0 |
| SDGR | Schrödinger | Physik- und ML-Software für Moleküle | SDGR | 21 | 0 |
| RXRX | Recursion | KI-erst-Wirkstoffsuche, eigene Pipeline | RXRX | 21 | 0 |
| SLP | Simulations Plus | Biosimulation, Nischenanbieter | SLP | 16 | 0 |
| SONY | Sony Group | SPAD-Detektor, Bildsensoren | 6758.T | 5 | 0 |
| LITE | Lumentum | Hochleistungslaser, VCSEL | LITE | 20 | 0 |
| STM | STMicroelectronics | SPAD-Detektoren, Fertigung | STM | 5 | 0 |
| ON | onsemi | SiPM- und SPAD-Arrays | ON | 21 | 0 |
| AMSOSR | ams OSRAM | VCSEL-Laser, dToF-Module | AMS.SW | 5 | 0 |
| HSAI | Hesai Group | LiDAR, Volumenführer | HSAI | 5 | 0 |
| OUST | Ouster | LiDAR für Industrie, Robotik | OUST | 20 | 0 |
| ROBOSENSE | RoboSense | LiDAR, Robotik-Marktführer | 2498.HK | 4 | 0 |
| AEVA | Aeva Technologies | FMCW-LiDAR mit Tempomessung | AEVA | 20 | 0 |
| INVZ | Innoviz | Solid-State-LiDAR | INVZ | 6 | 0 |
| QCOM | Qualcomm | Sparsame Roboter-Recheneinheit | QCOM | 20 | 0 |
| AMBA | Ambarella | Edge-KI-Chips für Kameras | AMBA | 20 | 0 |
| MBLY | Mobileye | Fahrassistenz, Wahrnehmung | MBLY | 20 | 0 |
| ABB | ABB | Industrieroboter, Antriebe | ABBNY | 5 | 0 |
| ISRG | Intuitive Surgical | Chirurgieroboter | ISRG | 20 | 0 |
| AAPL | Apple | Endgeräte, kaum KI-Infrastruktur | AAPL | 20 | 10 |

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
28. Deshalb laufen beide über 2330.TW und 6758.T. Erst danach wird gemeinsam in
Dollar umgerechnet.

**Vierte Quartale.** Sie stehen nicht separat im XBRL und müssen als
Geschäftsjahr minus Neunmonatszeitraum rekonstruiert werden. Für Umsatz und
Gewinn ist das meistens exakt. Für gewichtete Aktienzahlen ist es sinnlos:
Amazon kam so auf 12 Millionen statt 10,9 Milliarden Aktien. Und manchmal geht
auch der Gewinn schief, siehe unten.

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

**Aktiengattungen.** Die Stammdaten von yfinance nennen für Alphabet 5,87
Milliarden Aktien; aus Nettogewinn und Gewinn je Aktie folgen 12,2 Milliarden.
Die zweite Gattung fehlt, und mit ihr die halbe Marktkapitalisierung. Dell
dasselbe Muster.

**Splits treffen Kurs und Filing verschieden.** Der Kurs aus yfinance ist
splitbereinigt, der Gewinn je Aktie aus dem Filing steht so da, wie er
eingereicht wurde. Bei KLA liegt zwischen beiden der Faktor zehn, und das KGV
kommt auf 7 statt 52.

**ADS gegen Stammaktie.** Hesai meldet den Gewinn je ADS, die Aktienzahl zählt
aber Stammaktien. Faktor sieben im Nenner.

**Zwei Periodenraster nebeneinander.** Nebius reicht bei der SEC zu Ende
Februar, Mai, August und November ein; yfinance liefert daneben
Kalenderquartale. Beide Reihen zusammen ergeben Quartale, die einander
überlappen, und jede Summe über vier Quartale zählt doppelt.

---

## Reparatur

Die letzten vier Fallstricke stecken noch in der Extraktion. Bis die Pipeline
sie nicht mehr macht, läuft `reparatur.py` nach jedem Export über die fertige
Datei:

    python reparatur.py                 nur berichten, nichts ändern
    python reparatur.py --anwenden      Datei überschreiben
    python reparatur.py --alle          jeden Eingriff einzeln auflisten

Fünf Regeln, jede auf einen beobachteten Fehler zugeschnitten, jede mit einer
Gegenprobe, damit sie nicht selbst danebengreift:

| Regel | was sie tut | Umfang im aktuellen Stand |
|---|---|---|
| R1 | negative Aktienzahlen aus der Q4-Rekonstruktion leeren | 54 Quartale in 14 Firmen |
| R2 | Aktienzahl ersetzen, wenn eine Gattung fehlt und die abgeleitete Zahl zur Marktkapitalisierung von yfinance passt | Alphabet, Dell |
| R3 | Vorzeichenkonflikt zwischen Nettogewinn und Gewinn je Aktie auflösen | 18 Quartale in 11 Firmen |
| R4 | Gewinn je Aktie neu rechnen, wenn er durchgehend auf fremder Aktienbasis steht und die Rechnung näher am Marktbild liegt | KLA, Hesai |
| R5 | von zwei überlappenden Quartalsenden das aus der Einreichung behalten | Nebius, 5 Quartale |

Danach werden alle abgeleiteten Größen neu gerechnet: Gewinn je Aktie über vier
Quartale, Umsatz über vier Quartale, beide KGV, Marktkapitalisierung,
Kurs-Umsatz-Verhältnis.

Bei R3 entscheidet die Nachbarschaft, welche der beiden Zahlen die kaputte ist.
Kippt der Nettogewinn eines Quartals gegen alle Nachbarquartale, ist er es und
wird geleert; Arista weist so für drei vierte Quartale Milliardenverluste aus,
die es nie gab. Passt er zu den Nachbarn, liegt der Fehler beim Gewinn je Aktie,
und der wird aus Nettogewinn und Aktienzahl gerechnet; Nvidia stand im Quartal
zum Januar 2023 mit minus 1,00 je Aktie bei 1,4 Milliarden Gewinn.

Was die Reparatur bewirkt, in Zahlen: negative Aktienzahlen von 54 auf null,
Vorzeichenkonflikte von 18 auf null, überlappende Perioden von 5 auf null.
Firmen, deren KGV um mehr als ein Drittel nach unten oder um mehr als zwei
Drittel nach oben vom KGV aus yfinance abweicht, von fünf auf zwei: KLA von 7,1
auf 52,2 bei 50,0 aus yfinance, Hesai von 5,7 auf 39,5 bei 34,5, Nebius von
497,7 auf leer, weil die vier bereinigten Quartale zusammen einen Verlust
ergeben. Übrig bleiben Astera Labs und SanDisk. Dort liegt kein
Extraktionsfehler vor, die Zahlen stimmen mit den Filings überein; yfinance
rechnet dort mit einer anderen Gewinngröße als dem GAAP-Nettogewinn.

---

## Bekannte Grenzen

**Nettogewinn je Segment gibt es nicht.** Über acht Firmen geprüft: Umsatz und
operatives Ergebnis tragen eine Segmentdimension, Nettogewinn, Steuern und
Zinsen bei keiner einzigen. Der Standard verlangt nur die Größe, die die
Konzernleitung je Segment tatsächlich steuert. Zinsen, Steuern und
Beteiligungsergebnisse liegen auf Konzernebene.

**Samsungs Segmente fehlen.** Die Segmenttabelle liegt in den Präsentationen als
Grafik vor; die Textebene lässt sich nicht verlässlich den Zeilen zuordnen.
Statt womöglich falscher Zahlen steht dort ein Hinweis. Ausgerechnet bei
Samsung wäre die Aufteilung besonders interessant, weil der Konzernumsatz das
Speichergeschäft hinter Handys versteckt.

**Samsungs Marktkapitalisierung** liegt hier 23 Prozent unter der von yfinance.
Die Aktienzahl stimmt mit dem eigenen Gewinn je Aktie überein, yfinance rechnet
die Vorzugsaktien mit. Nicht angefasst, weil beide Lesarten vertretbar sind.

**Mobileye und Recursion** melden den Verlust je Aktie auf allen Gattungen, die
Aktienzahl in den Stammdaten zählt nur eine. Der Verlust je Aktie ist deshalb
kleiner, als der Nettogewinn geteilt durch die tatsächliche Aktienzahl wäre. R2
greift nicht, weil die Marktkapitalisierung von yfinance dieselbe
Teilbetrachtung hat und die Gegenprobe damit ins Leere läuft.

**Sony hat nur fünf Quartale**, weil dort kein Quartals-XBRL bei der SEC
eingereicht wird. **CoreWeave hat neun**, der Börsengang war im März 2025.
**Kioxia und RoboSense** berichten halbjährlich; im Quartalsraster stehen dort
Lücken von einem halben Jahr.

**Bei KLA, Lam Research und Monolithic Power** fehlen im jüngsten Quartal Umsatz
und Nettogewinn, weil zum Zeitpunkt des Exports nur der Gewinn je Aktie
vorlag. Das Kurs-Umsatz-Verhältnis bleibt dort leer.

Keine Anlageberatung. Zahlen können Extraktionsfehler enthalten; die
Filing-Quelle steht in jeder Quartalszeile.

---

<a name="english"></a>

## English

Valuation and quarterly results for 66 listed companies along Nvidia's supply
chain, customer base and demand side. A single HTML file, no server, no build
step, no dependencies. Available in German, English and Mongolian via the switch
at the top left.

**➜ [Open the interactive page](https://mendeltem.github.io/AI_Companys/nvidia-oekosystem.html)**

Data as of 6 August 2026: 1069 quarters from 2019-02 to 2026-07, plus 47,839
daily closing prices across three years.

**Everything is in US dollars.** Ten companies do not report in dollars: TSMC,
UMC, ASE and Hon Hai in TWD, SK hynix and Samsung in KRW, Kioxia and Sony in
JPY, ams OSRAM in CHF, RoboSense in HKD. Their prices and quarterly figures are
converted at the rate of the data date, price and earnings per share with the
same factor, which is why P/E, price to sales, margins and growth rates are
untouched by it. The factor is fixed rather than historical per day, so the
price curves keep their shape. Prices come from each company's home exchange
rather than its ADR, because that is the only way price and earnings per share
share a currency in the first place.

Quarterly figures come from SEC XBRL, from yfinance, and from the original press
releases and earnings presentations of TSMC, Samsung and SK hynix; the source is
named in every quarterly row. Segment figures are pulled from the XBRL instances
of individual filings, because the companyfacts API only exposes consolidated
values.

Two valuation measures sit side by side: the trailing four-quarter P/E, and the
latest quarter's earnings times four. For fast-growing companies the two diverge
sharply, and where a one-off distorts the annual sum, the second measure is the
one that still says something.

`reparatur.py` repairs five classes of extraction error in the finished file:
negative share counts from reconstructed fourth quarters, missing share classes,
sign conflicts between net profit and earnings per share, earnings per share on
a different share basis than the price, and two overlapping period grids in one
series. Each rule carries a cross-check so it cannot make things worse. Run it
after every export.

Net profit by segment is not shown because it does not exist in the filings.
Checked across eight companies: revenue and operating profit carry a segment
dimension, net profit, tax and interest carry none. Accounting standards only
require the measure management actually steers per segment, which is operating
profit.

Not investment advice. Figures may contain extraction errors.
