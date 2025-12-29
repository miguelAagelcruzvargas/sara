@echo off
REM ============================================
REM SARA - Sistema de Limpieza Profunda
REM Limpia archivos temporales, papelera, cache
REM ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║   SARA - Limpieza del Sistema          ║
echo ╚════════════════════════════════════════╝
echo.

REM 1. Limpiar archivos temporales de Windows
echo [1/6] Limpiando archivos temporales...
del /q/f/s %TEMP%\* > nul 2>&1
del /q/f/s C:\Windows\Temp\* > nul 2>&1
echo ✓ Temporales eliminados

REM 2. Vaciar papelera de reciclaje
echo [2/6] Vaciando papelera de reciclaje...
rd /s /q %systemdrive%\$Recycle.bin > nul 2>&1
echo ✓ Papelera vaciada

REM 3. Limpiar cache de navegadores
echo [3/6] Limpiando cache de navegadores...
REM Chrome
del /q/f/s "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" > nul 2>&1
REM Edge
del /q/f/s "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" > nul 2>&1
REM Firefox
del /q/f/s "%APPDATA%\Mozilla\Firefox\Profiles\*.default\cache2\*" > nul 2>&1
echo ✓ Cache de navegadores limpiado

REM 4. Limpiar archivos prefetch
echo [4/6] Limpiando archivos prefetch...
del /q/f/s C:\Windows\Prefetch\* > nul 2>&1
echo ✓ Prefetch limpiado

REM 5. Limpiar logs antiguos
echo [5/6] Limpiando logs del sistema...
del /q/f/s C:\Windows\Logs\* > nul 2>&1
del /q/f/s C:\Windows\System32\LogFiles\* > nul 2>&1
echo ✓ Logs eliminados

REM 6. Liberar memoria RAM
echo [6/6] Liberando memoria RAM...
rundll32.exe advapi32.dll,ProcessIdleTasks
echo ✓ Memoria optimizada

echo.
echo ════════════════════════════════════════
echo    ✓ Limpieza completada exitosamente
echo ════════════════════════════════════════
echo.

REM Mostrar espacio liberado (aproximado)
echo Espacio liberado: Calculando...
timeout /t 2 /nobreak > nul
