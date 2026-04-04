@echo off
setlocal

set "REPO_ROOT=%~dp0"
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"

start "NBA Oracle API" powershell.exe -NoExit -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\start_nba_oracle_backend.ps1"
start "NBA Oracle Tunnel" powershell.exe -NoExit -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\start_nba_oracle_tunnel.ps1"

echo NBA Oracle hosted stack launch requested.
echo API and tunnel terminals should now be opening.

endlocal
