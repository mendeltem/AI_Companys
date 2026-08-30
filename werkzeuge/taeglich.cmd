@echo off
REM Taeglicher Lauf: nachsehen, was neu bei der SEC eingereicht wurde, holen,
REM Text ziehen, stueckeln. Wird von der Aufgabenplanung um 05:00 gestartet.
REM Von Hand aufrufen geht genauso - der Lauf merkt sich, was er schon hat.
REM
REM Protokoll:  AI_companys_berichte\laeufe\JJJJ-MM-TT.md   (was neu war)
REM             AI_companys_berichte\laeufe\lauf.log        (roher Ausgabestrom)

setlocal
set WURZEL=%~dp0..
set ZIEL=%WURZEL%\..\AI_companys_berichte
if not exist "%ZIEL%\laeufe" mkdir "%ZIEL%\laeufe"

echo. >> "%ZIEL%\laeufe\lauf.log"
echo ===== %DATE% %TIME% ===== >> "%ZIEL%\laeufe\lauf.log"
python "%WURZEL%\werkzeuge\berichte.py" taeglich >> "%ZIEL%\laeufe\lauf.log" 2>&1
echo Beendet mit %ERRORLEVEL% >> "%ZIEL%\laeufe\lauf.log"
endlocal
