@echo off
REM Exemple:   startnodes.bat config.txt 0 4

if "%~3"=="" (
    echo Utilizare: startnodes.bat config.txt primul_index ultimul_index
    echo Exemplu:   startnodes.bat config.txt 0 4
    exit /b 1
)

set CONFIG=%~1
set FIRST=%~2
set LAST=%~3

echo Pornesc nodurile %FIRST% pana la %LAST% cu config: %CONFIG%

for /L %%i in (%FIRST%,1,%LAST%) do (
    echo Pornesc nodul %%i...
    start "Nod %%i" python bcastnode.py %CONFIG% %%i
)

echo Toate nodurile au fost pornite!
echo Nodurile vor astepta 15 secunde inainte de a incepe broadcasting-ul.