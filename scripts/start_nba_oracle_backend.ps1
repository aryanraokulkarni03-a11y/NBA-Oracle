. (Join-Path $PSScriptRoot "nba_oracle_common.ps1")

$repoRoot = Get-NbaOracleRepoRoot

Set-Location $repoRoot
Write-Host "Starting NBA Oracle API from $repoRoot"

Invoke-NbaOraclePython -Arguments @("main.py", "serve-api")
