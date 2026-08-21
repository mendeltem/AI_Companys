# -*- coding: utf-8 -*-
"""Repariert bekannte Extraktionsfehler im Datenblock von nvidia-oekosystem.html.

Die Fehler entstehen nicht in der Seite, sondern eine Stufe frueher, beim Ziehen
der Zahlen aus XBRL und yfinance. Bis die Pipeline sie nicht mehr macht, laeuft
dieses Skript nach jedem Export ueber die fertige Datei:

    python reparatur.py                 nur berichten, nichts aendern
    python reparatur.py --anwenden      Datei ueberschreiben

Fuenf Regeln, jede auf einen beobachteten Fehler zugeschnitten:

R1  Negative Aktienzahlen. Das vierte Quartal wird als Geschaeftsjahr minus
    Neunmonatszeitraum rekonstruiert. Fuer Umsatz und Gewinn stimmt das, fuer
    gewichtete Aktienzahlen nicht: dort kommt eine Differenz zweier Bestaende
    heraus, die negativ sein kann. Solche Werte werden geleert.

R2  Fehlende Aktiengattungen. Alphabet steht mit 5,87 Mrd Aktien in den
    Stammdaten, aus Nettogewinn und Gewinn je Aktie folgen aber 12,2 Mrd; die
    zweite Gattung fehlt. Ergebnis waere eine halbierte Marktkapitalisierung.
    Ersetzt wird nur, wenn die aus dem Gewinn abgeleitete Zahl auch zur
    Marktkapitalisierung von yfinance passt, sonst liegt der Fehler beim
    Gewinn je Aktie und nicht bei der Aktienzahl.

R3  Vorzeichenkonflikt zwischen Nettogewinn und Gewinn je Aktie. Beide koennen
    nicht gleichzeitig stimmen. Ist die Nettomarge des Quartals gegenueber den
    uebrigen Quartalen der Firma voellig aus dem Rahmen, ist der Nettogewinn
    die kaputte Seite und wird geleert; sonst der Gewinn je Aktie, der dann aus
    Nettogewinn und Aktienzahl neu gerechnet wird.

R4  Gewinn je Aktie auf fremder Basis. Bei KLA stehen 9,12 je Quartal neben
    einem Nettogewinn von 1,2 Mrd auf 1,31 Mrd Aktien, also dem Zehnfachen des
    rechnerischen Werts: der Kurs ist splitbereinigt, die Zahl aus dem Filing
    nicht. Bei Hesai liegt der Faktor bei sieben, dort steht der Gewinn je
    Aktie je ADS. Weicht der Wert um mehr als Faktor drei von Nettogewinn durch
    Aktienzahl ab, gilt die Rechnung.

R5  Zwei Periodenraster nebeneinander. Bei Nebius liegen Quartale zum Monatsende
    Februar, Mai, August, November aus der SEC-Einreichung und daneben
    Kalenderquartale aus yfinance. Sie ueberlappen, und jede Summe ueber vier
    Quartale zaehlt doppelt. Von zwei Enden, die weniger als 60 Tage
    auseinanderliegen, bleibt das aus der Einreichung stehen.

Danach werden alle abgeleiteten Groessen neu gerechnet, die auf den geaenderten
Zahlen stehen: Gewinn je Aktie ueber vier Quartale, Umsatz ueber vier Quartale,
beide KGV, Marktkapitalisierung, Kurs-Umsatz-Verhaeltnis.
"""
import json
import os
import re
import statistics as st
import sys

DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nvidia-oekosystem.html')
ANWENDEN = '--anwenden' in sys.argv

bericht = []


def melde(regel, firma, text):
    bericht.append((regel, firma, text))


def quartale_sortiert(e):
    return sorted(e['quartale'], key=lambda z: z['ende'], reverse=True)


def aktien_des_quartals(e, z):
    a = z.get('aktien')
    return a if (a and a > 0) else e.get('aktien_zahl')


# ---------------------------------------------------------------- Datei lesen
roh = open(DATEI, encoding='utf-8').read()
treffer = re.search(r'(<script[^>]*id="daten"[^>]*>)(.*?)(</script>)', roh, re.S)
D = json.loads(treffer.group(2))
F, K = D['firmen'], D['kurse']

# ------------------------------------------------- R1 negative Aktienzahlen
for k, e in F.items():
    for z in e['quartale']:
        if z.get('aktien') is not None and z['aktien'] < 0:
            melde('R1', k, '%s Aktienzahl %.4g geleert' % (z['ende'], z['aktien']))
            z['aktien'] = None

# ------------------------------------------------- R2 Aktienzahl der Firma
for k, e in F.items():
    q = quartale_sortiert(e)
    abgeleitet = [z['netto'] / z['eps'] for z in q[:4]
                  if z.get('netto') and z.get('eps')]
    if len(abgeleitet) < 3 or not e.get('aktien_zahl') or not e.get('marktkap_yf'):
        continue
    kandidat = st.median(abgeleitet)
    if abs(e['aktien_zahl'] / kandidat - 1) <= 0.25:
        continue                                   # Stammdaten sind stimmig
    if abs(kandidat * e['kurs'] / e['marktkap_yf'] - 1) > 0.25:
        continue                                   # Kandidat passt nicht zum Markt
    melde('R2', k, 'Aktienzahl %.4g -> %.4g (aus Nettogewinn und Gewinn je Aktie)'
          % (e['aktien_zahl'], kandidat))
    e['aktien_zahl'] = kandidat
    e['aktien_quelle'] = 'Nettogewinn durch Gewinn je Aktie'

# ------------------------------------------------- R3 Vorzeichenkonflikte
for k, e in F.items():
    reihe = sorted(e['quartale'], key=lambda z: z['ende'])
    for i, z in enumerate(reihe):
        n, ep = z.get('netto'), z.get('eps')
        if n is None or ep is None or n == 0 or ep == 0 or (n > 0) == (ep > 0):
            continue
        # Welche der beiden Zahlen ist die kaputte? Der Nettogewinn steht in
        # einer Reihe; kippt nur dieses eine Quartal gegen alle Nachbarn, ist er
        # es. Passt er zu den Nachbarn, liegt der Fehler beim Gewinn je Aktie.
        nachbarn = [y.get('netto') for y in reihe[max(0, i - 2):i] + reihe[i + 1:i + 3]]
        nachbarn = [v for v in nachbarn if v]
        if len(nachbarn) >= 2 and all((v > 0) != (n > 0) for v in nachbarn):
            melde('R3', k, '%s Nettogewinn %.4g geleert, kippt gegen alle %d Nachbarquartale'
                  % (z['ende'], n, len(nachbarn)))
            z['netto'] = None
            z['nettomarge'] = None
        else:
            a = aktien_des_quartals(e, z)
            if not a:
                continue
            melde('R3', k, '%s Gewinn je Aktie %.2f -> %.2f (aus Nettogewinn)'
                  % (z['ende'], ep, n / a))
            z['eps'] = n / a
            z['eps_berechnet'] = True

# ------------------------------------------------- R4 fremde Aktienbasis
for k, e in F.items():
    getroffen = []
    for z in e['quartale']:
        n, ep = z.get('netto'), z.get('eps')
        a = aktien_des_quartals(e, z)
        if n is None or ep is None or ep == 0 or not a:
            continue
        gerechnet = n / a
        if gerechnet == 0:
            continue
        if abs(ep / gerechnet) > 3 or abs(gerechnet / ep) > 3:
            getroffen.append((z, ep, gerechnet))
    # Einzelne Ausreisser sind Sondereffekte, ein durchgehender Faktor ist eine
    # andere Aktienbasis. Erst ab der Haelfte der Quartale wird gerechnet.
    if len(getroffen) < max(3, len(e['quartale']) // 2):
        continue
    # Gegenprobe, damit die Regel nicht selbst danebengreift: die Rechnung haengt
    # an der Aktienzahl, und wenn die falsch ist, wird es schlimmer statt besser.
    # Das neue KGV muss naeher am KGV von yfinance liegen als das alte.
    ersatz = {id(z): g for z, _, g in getroffen}
    q4 = quartale_sortiert(e)[:4]
    eps_neu = [ersatz.get(id(z), z.get('eps')) for z in q4]
    if not e.get('kgv_yf') or len(eps_neu) < 4 or any(v is None for v in eps_neu):
        continue
    summe = sum(eps_neu)
    if summe <= 0 or not e.get('kgv_ttm'):
        continue
    kgv_neu = e['kurs'] / summe
    if abs(kgv_neu / e['kgv_yf'] - 1) >= abs(e['kgv_ttm'] / e['kgv_yf'] - 1):
        melde('R4', k, 'Verdacht auf andere Aktienbasis, aber die Rechnung trifft das '
                       'Marktbild schlechter als der gemeldete Wert; nichts geaendert')
        continue
    melde('R4', k, '%d von %d Quartalen auf anderer Aktienbasis, Faktor rund %.1f, KGV %.1f -> %.1f (yfinance %.1f)'
          % (len(getroffen), len(e['quartale']),
             st.median([abs(a / b) for _, a, b in getroffen]),
             e['kgv_ttm'], kgv_neu, e['kgv_yf']))
    for z, _, gerechnet in getroffen:
        z['eps'] = gerechnet
        z['eps_berechnet'] = True

# ------------------------------------------------- R5 doppeltes Periodenraster
for k, e in F.items():
    from datetime import date
    q = sorted(e['quartale'], key=lambda z: z['ende'])
    weg = []
    for a, b in zip(q, q[1:]):
        if (date.fromisoformat(b['ende']) - date.fromisoformat(a['ende'])).days >= 60:
            continue
        # Das Quartal aus der Einreichung bleibt, das aus yfinance geht.
        opfer = b if 'yfinance' in str(b.get('quelle')) and 'XBRL' not in str(b.get('quelle')) else a
        if 'XBRL' in str(opfer.get('quelle')):
            continue
        if not any(o is opfer for o in weg):
            weg.append(opfer)
    for z in weg:
        melde('R5', k, '%s aus %s entfernt, ueberlappt mit dem Quartal aus der Einreichung'
              % (z['ende'], z.get('quelle')))
    if weg:
        e['quartale'] = [z for z in e['quartale'] if not any(o is z for o in weg)]
        e['n_quartale'] = len(e['quartale'])

# ------------------------------------------------- abgeleitete Groessen neu
for k, e in F.items():
    q = quartale_sortiert(e)
    e['quartale'] = q
    q4 = q[:4]
    eps4 = [z.get('eps') for z in q4]
    ums4 = [z.get('umsatz') for z in q4]
    e['eps_q'] = q[0].get('eps') if q else None
    e['eps_ttm'] = sum(eps4) if len(eps4) == 4 and all(v is not None for v in eps4) else None
    e['umsatz_ttm'] = sum(ums4) if len(ums4) == 4 and all(v is not None for v in ums4) else None
    if e.get('aktien_zahl') and e.get('kurs'):
        e['marktkap'] = e['kurs'] * e['aktien_zahl']
        if e.get('fx_usd'):
            e['marktkap_usd'] = e['marktkap'] * e['fx_usd']
    e['kgv_ttm'] = (e['kurs'] / e['eps_ttm']) if e.get('eps_ttm') and e['eps_ttm'] > 0 else None
    e['kgv_q4x'] = (e['kurs'] / (e['eps_q'] * 4)) if e.get('eps_q') and e['eps_q'] > 0 else None
    if e.get('umsatz_ttm') and e.get('marktkap'):
        e['kuv'] = e['marktkap'] / e['umsatz_ttm']
        if e.get('fx_usd'):
            e['umsatz_ttm_usd'] = e['umsatz_ttm'] * e['fx_usd']
    else:
        e['kuv'] = None
    e['n_quartale'] = len(e['quartale'])

# ------------------------------------------------------------------ Bericht
for regel in ('R1', 'R2', 'R3', 'R4', 'R5'):
    zeilen = [b for b in bericht if b[0] == regel]
    if not zeilen:
        continue
    print('=== %s: %d Eingriffe in %d Firmen ===' % (regel, len(zeilen), len({z[1] for z in zeilen})))
    grenze = len(zeilen) if '--alle' in sys.argv else 12
    for _, firma, text in zeilen[:grenze]:
        print('    %-10s %s' % (firma, text))
    if len(zeilen) > grenze:
        print('    ... und %d weitere, mit --alle vollstaendig' % (len(zeilen) - grenze))

print('\nKGV nach der Reparatur gegen das von yfinance:')
print('    %-10s %10s %10s %7s' % ('TICK', 'eigen', 'yfinance', 'Faktor'))
for k, e in sorted(F.items()):
    a, b = e.get('kgv_ttm'), e.get('kgv_yf')
    if not a or not b or a < 0 or b < 0:
        continue
    if not 0.6 < a / b < 1.7:
        print('    %-10s %10.1f %10.1f %7.2f' % (k, a, b, a / b))

if ANWENDEN:
    neu = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    roh = roh[:treffer.start(2)] + neu + roh[treffer.end(2):]
    open(DATEI, 'w', encoding='utf-8', newline='').write(roh)
    print('\nDatei geschrieben.')
else:
    print('\nNichts geaendert. Mit --anwenden schreiben.')
