# -*- coding: utf-8 -*-
"""Taegliche Pflege der veroeffentlichten Seite.

Die erzeugende Pipeline schreibt nvidia-oekosystem.html vollstaendig neu und
laedt sie hoch. Alles, was hier ergaenzt wird - innerer Wert, Renditekacheln,
Gruppen -, ist danach weg. Dieser Lauf traegt es wieder auf.

Die Reihenfolge ist der ganze Trick:

    holen  ->  auftragen  ->  pushen

Nie umgekehrt. Wer eine aeltere Kopie bearbeitet und dann pusht, wirft die
frischere Fassung der Pipeline weg. Genau das hat GitHub am 30. August
abgelehnt, und die Ablehnung war das Beste, was an dem Tag passiert ist.

Gearbeitet wird in einem eigenen Arbeitsbaum, nicht im Arbeitsverzeichnis:
Der Lauf um sechs Uhr weiss nicht, woran gerade jemand sitzt, und darf weder
den Zweig wechseln noch ungesicherte Aenderungen anfassen.

    python werkzeuge/taeglich_seite.py            # holen, auftragen, pushen
    python werkzeuge/taeglich_seite.py --pruefen  # nichts schreiben
    python werkzeuge/taeglich_seite.py --wert     # Wertrechnung erzwingen
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402

BAUM = b._pfad("seitenbaum")
ZWEIG = "main"
# Die Jahresabschluesse, aus denen der innere Wert kommt, aendern sich vier Mal
# im Jahr. Sechsundsechzig Abrufe bei der SEC dafuer jeden Morgen waeren
# Verschwendung; einmal die Woche reicht und faengt jede Meldung rechtzeitig.
WERT_TAGE = 7


def _git(pfad, *args, pruefen=True):
    erg = subprocess.run(["git", "-C", pfad] + list(args), capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    if pruefen and erg.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), (erg.stderr or erg.stdout).strip()[:400]))
    return (erg.stdout or "").strip()


def _baum_bereit():
    """Arbeitsbaum auf dem Stand des Fernzweigs, notfalls neu angelegt."""
    if not os.path.exists(os.path.join(BAUM, ".git")):
        os.makedirs(os.path.dirname(BAUM), exist_ok=True)
        _git(b.WURZEL, "worktree", "add", BAUM, ZWEIG)
    _git(BAUM, "fetch", "origin", ZWEIG)
    # Hart auf den Fernstand: In diesem Verzeichnis arbeitet niemand von Hand,
    # es gibt hier also nichts zu retten - und alles andere waere ein Merge,
    # der um sechs Uhr morgens niemanden findet, der ihn aufloest.
    _git(BAUM, "reset", "--hard", "origin/" + ZWEIG)
    return BAUM


def _lauf(befehl, *args):
    umgebung = dict(os.environ, BERICHTE_ZIEL=b.ZIEL, PYTHONIOENCODING="utf-8")
    erg = subprocess.run([sys.executable, os.path.join(BAUM, "werkzeuge", befehl)] + list(args),
                         cwd=BAUM, env=umgebung, capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    return erg.returncode, (erg.stdout or "") + (erg.stderr or "")


def _wert_faellig():
    p = b._pfad("wert.json")
    if not os.path.exists(p):
        return True
    alter = datetime.now() - datetime.fromtimestamp(os.path.getmtime(p))
    return alter > timedelta(days=WERT_TAGE)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pruefen", action="store_true", help="nichts schreiben, nur berichten")
    p.add_argument("--wert", action="store_true", help="Wertrechnung erzwingen")
    p.add_argument("--ohne-push", action="store_true", help="committen, aber nicht pushen")
    args = p.parse_args()

    zeilen = ["# Seitenlauf %s" % date.today().isoformat(), ""]

    def sag(t):
        print(t)
        zeilen.append(t)

    try:
        _baum_bereit()
        sag("Arbeitsbaum auf origin/%s: %s" % (ZWEIG, _git(BAUM, "log", "--oneline", "-1")))
    except Exception as f:
        sag("Arbeitsbaum nicht bereit: %s" % f)
        _protokoll(zeilen)
        return 1

    # 1. Was seit gestern eingereicht wurde: holen, Text ziehen, stueckeln.
    # Steht vor allem anderen, damit die Analyse spaeter auf dem frischesten
    # Material arbeitet.
    code, aus = _lauf("berichte.py", "taeglich", *(["--nur-pruefen"] if args.pruefen else []))
    neue = [z for z in aus.splitlines() if z.startswith("- ") or "neue Dokumente" in z]
    sag("Einreichungen geprueft (Code %d): %s"
        % (code, (neue[0][:100] if neue else "keine neuen")))
    for z in neue[1:9]:
        sag("  " + z[:110])

    if args.wert or _wert_faellig():
        code, aus = _lauf("wert.py")
        letzte = [z for z in aus.splitlines() if z.strip()][-1:] or [""]
        sag("Wertrechnung gelaufen (Code %d): %s" % (code, letzte[0][:90]))
    else:
        sag("Wertrechnung uebersprungen, wert.json juenger als %d Tage" % WERT_TAGE)

    code, aus = _lauf("seite.py", *(["--pruefen"] if args.pruefen else []))
    if code != 0:
        sag("Auftragen fehlgeschlagen:\n" + aus[-600:])
        _protokoll(zeilen)
        return 1
    for z in aus.splitlines():
        if z.strip().startswith(("Innerer Wert", "   ")):
            sag("  " + z.strip())

    if args.pruefen:
        sag("--pruefen: nichts geschrieben.")
        _protokoll(zeilen)
        return 0

    # Erst hinzufuegen, dann pruefen. Umgekehrt geht es schief: git meldet die
    # Datei im Arbeitsverzeichnis als geaendert, weil sich die Zeilenenden
    # unterscheiden, normalisiert sie beim Hinzufuegen und hat danach nichts
    # mehr zu committen. Der Lauf waere an jedem Tag gescheitert, an dem sich
    # inhaltlich nichts aendert - also an den meisten.
    _git(BAUM, "add", "-A")
    if not _git(BAUM, "diff", "--cached", "--name-only"):
        sag("Seite unveraendert - kein Commit.")
        _protokoll(zeilen)
        return 0

    _git(BAUM, "commit", "-m",
         "Kennzahlen nachgetragen %s\n\nMaschinell: innerer Wert, Renditekacheln und Gruppen "
         "nach dem taeglichen Upload wieder aufgetragen.\n\nCo-Authored-By: Claude Opus 5 "
         "<noreply@anthropic.com>" % date.today().isoformat())
    sag("Committet: " + _git(BAUM, "log", "--oneline", "-1"))

    if args.ohne_push:
        sag("Ohne Push.")
        _protokoll(zeilen)
        return 0

    # Ein Wiederholversuch: Faellt zwischen Holen und Pushen ein Upload der
    # Pipeline herein, wird der Push abgelehnt. Dann von vorn - holen,
    # auftragen, pushen. Beim zweiten Fehlschlag Schluss; erzwungen wird hier
    # nichts, dafuer ist der Verlust zu gross.
    for versuch in (1, 2):
        try:
            _git(BAUM, "push", "origin", ZWEIG)
            sag("Gepusht nach origin/%s" % ZWEIG)
            _protokoll(zeilen)
            return 0
        except Exception as f:
            sag("Push abgelehnt (Versuch %d): %s" % (versuch, str(f)[:200]))
            if versuch == 2:
                break
            sag("Neu holen und noch einmal auftragen.")
            try:
                _baum_bereit()
                code, aus = _lauf("seite.py")
                _git(BAUM, "add", "-A")
                if code != 0 or not _git(BAUM, "diff", "--cached", "--name-only"):
                    sag("Nach dem Neuholen nichts zu tun.")
                    _protokoll(zeilen)
                    return 0
                _git(BAUM, "commit", "-m", "Kennzahlen nachgetragen %s\n\nCo-Authored-By: "
                     "Claude Opus 5 <noreply@anthropic.com>" % date.today().isoformat())
            except Exception as f2:
                sag("Zweiter Anlauf gescheitert: %s" % f2)
                break
    sag("Nicht gepusht. Der Commit liegt in %s und laesst sich nachschieben." % BAUM)
    _protokoll(zeilen)
    return 1


def _protokoll(zeilen):
    os.makedirs(b._pfad("laeufe"), exist_ok=True)
    ziel = b._pfad("laeufe", "seite-%s.md" % date.today().isoformat())
    open(ziel, "w", encoding="utf-8").write("\n".join(zeilen) + "\n")


if __name__ == "__main__":
    sys.exit(main())
