<#
    Zweiter llama-server, nur fuer Einbettungen, auf einem eigenen Port.

    Getrennt vom Chatserver auf 8080, damit beide nebeneinander laufen koennen:
    das Einbetten von hunderttausend Stuecken darf den Chat nicht blockieren,
    und ein Modellwechsel auf 8080 darf die Vektoren nicht ungueltig machen.

    Ein Einbettungsmodell ist klein und dicht, also kein -ncmoe noetig: es passt
    ganz auf die Karte und laesst dem grossen Modell trotzdem Luft.

    Wichtig: -ub muss mindestens so gross sein wie das laengste Stueck in Token.
    Ist es kleiner, bricht llama-server die Anfrage ab, statt zu kuerzen. Ein
    Stueck von 1200 Zeichen sind grob 400 Token, 512 genuegt also.

    Platzfrage: Auf einer 8-GB-Karte, auf der schon das grosse Chatmodell liegt
    (rund 6,7 GB), bleiben etwa 1,2 GB. Das Modell wiegt 640 MB, der Rest geht
    fuer KV-Cache und Rechenpuffer drauf - und der Rechenpuffer haengt an -ub.
    Deshalb hier 512 und Kontext 2048 statt der bequemen 2048/4096. Wer die
    Karte allein hat, setzt beides hoch und wird schneller.
#>
param(
    [int]$Ctx     = 2048,
    [int]$Port    = 8081,
    [int]$Batch   = 512,
    [int]$Threads = 8,
    [string]$Model = "C:\Users\Mendel\models\Qwen3-Embedding-0.6B-Q8_0.gguf",
    [string]$Exe   = "C:\Users\Mendel\llama.cpp\llama-server.exe",
    [ValidateSet("mean","cls","last","rank")]
    [string]$Pooling = "last"     # Qwen3-Embedding poolt ueber das letzte Token.
                                  # Fuer bge-m3 und Verwandte stattdessen "cls".
)

if (-not (Test-Path $Model)) {
    Write-Error "Einbettungsmodell fehlt: $Model"
    Write-Host ""
    Write-Host "Holen mit (rund 640 MB):" -ForegroundColor Yellow
    Write-Host '  curl -L -o "C:\Users\Mendel\models\Qwen3-Embedding-0.6B-Q8_0.gguf" `' -ForegroundColor DarkGray
    Write-Host '    https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF/resolve/main/Qwen3-Embedding-0.6B-Q8_0.gguf' -ForegroundColor DarkGray
    exit 1
}
if (-not (Test-Path $Exe)) { Write-Error "llama-server fehlt: $Exe"; exit 1 }

$srvArgs = @(
    "-m", $Model
    "--embedding"
    "--pooling", $Pooling
    "-ngl", "99"
    "-c", "$Ctx"
    "-b", "$Batch"
    "-ub", "$Batch"
    "-t", "$Threads"
    "-fa", "on"
    "--host", "127.0.0.1"
    "--port", "$Port"
)

Write-Host "Einbettungsserver: $(Split-Path $Model -Leaf)  Port $Port  Pooling $Pooling" -ForegroundColor Cyan
Write-Host "Test: python werkzeuge\berichte.py suchen `"HBM Kapazitaet ausverkauft`"" -ForegroundColor DarkGray
& $Exe @srvArgs
