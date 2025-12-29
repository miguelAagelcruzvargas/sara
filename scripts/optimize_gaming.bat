@echo off
REM ============================================
REM SARA - Optimización para Gaming
REM Cierra apps, libera RAM, prioridad alta
REM ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║   SARA - Modo Gaming Activado          ║
echo ╚════════════════════════════════════════╝
echo.

REM 1. Cerrar navegadores (consumen mucha RAM)
echo [1/5] Cerrando navegadores...
taskkill /F /IM chrome.exe /T > nul 2>&1
taskkill /F /IM msedge.exe /T > nul 2>&1
taskkill /F /IM firefox.exe /T > nul 2>&1
echo ✓ Navegadores cerrados

REM 2. Cerrar apps pesadas opcionales
echo [2/5] Cerrando apps pesadas...
taskkill /F /IM Discord.exe /T > nul 2>&1
taskkill /F /IM Spotify.exe /T > nul 2>&1
taskkill /F /IM Teams.exe /T > nul 2>&1
echo ✓ Apps pesadas cerradas

REM 3. Limpiar memoria RAM
echo [3/5] Liberando memoria RAM...
rundll32.exe advapi32.dll,ProcessIdleTasks
echo ✓ RAM optimizada

REM 4. Deshabilitar Windows Update temporalmente (opcional)
echo [4/5] Pausando servicios innecesarios...
net stop "wuauserv" > nul 2>&1
net stop "BITS" > nul 2>&1
echo ✓ Servicios pausados

REM 5. Limpiar archivos temporales rápido
echo [5/5] Limpieza rápida...
del /q/f/s %TEMP%\* > nul 2>&1
echo ✓ Limpieza completada

echo.
echo ════════════════════════════════════════
echo    ✓ Sistema optimizado para gaming
echo    ✓ Listo para jugar al máximo
echo ════════════════════════════════════════
echo.

REM Mostrar recursos disponibles
echo Recursos del sistema:
wmic OS get FreePhysicalMemory /value | find "FreePhysicalMemory"
wmic cpu get loadpercentage /value | find "LoadPercentage"
echo.
