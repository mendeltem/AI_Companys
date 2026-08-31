@echo off
REM Der taegliche Lauf um 06:00. Ein Eintrag in der Aufgabenplanung, ein
REM Protokoll, eine Stelle zum Nachsehen.
REM
REM   1. Was seit gestern bei der SEC eingereicht wurde: holen, Text ziehen.
REM   2. Innerer Wert neu rechnen, wenn die letzte Rechnung aelter als eine
REM      Woche ist - Jahresabschluesse aendern sich nicht taeglich.
REM   3. Die Ergaenzungen wieder auf die Seite auftragen, die die Pipeline
REM      inzwischen ueberschrieben haben koennte.
REM   4. Committen und pushen.
REM
REM Protokoll:  AI_companys_berichte\laeufe\JJJJ-MM-TT.md        (Einreichungen)
REM             AI_companys_berichte\laeufe\seite-JJJJ-MM-TT.md  (Seitenlauf)
REM             AI_companys_berichte\laeufe\lauf.log             (roher Strom)
REM
REM Von Hand geht genauso; der Lauf merkt sich, was er schon hat.

setlocal
set WURZEL=%~dp0..
set ZIEL=%WURZEL%\..\AI_companys_berichte
if not exist "%ZIEL%\laeufe" mkdir "%ZIEL%\laeufe"

echo. >> "%ZIEL%\laeufe\lauf.log"
echo ===== %DATE% %TIME% ===== >> "%ZIEL%\laeufe\lauf.log"
python "%WURZEL%\werkzeuge\taeglich_seite.py" >> "%ZIEL%\laeufe\lauf.log" 2>&1
echo Beendet mit %ERRORLEVEL% >> "%ZIEL%\laeufe\lauf.log"
endlocal
