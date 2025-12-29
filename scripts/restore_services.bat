@echo off
REM ============================================
REM SARA - Restaurar Servicios
REM Reactiva servicios pausados por gaming
REM ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║   SARA - Restaurando Sistema           ║
echo ╚════════════════════════════════════════╝
echo.

echo [1/2] Reactivando Windows Update...
net start "wuauserv" > nul 2>&1
net start "BITS" > nul 2>&1
echo ✓ Servicios reactivados

echo [2/2] Sistema restaurado
echo.
echo ════════════════════════════════════════
echo    ✓ Sistema en modo normal
echo ════════════════════════════════════════
echo.
