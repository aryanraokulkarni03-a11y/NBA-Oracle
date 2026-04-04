. (Join-Path $PSScriptRoot "nba_oracle_common.ps1")

$repoRoot = Get-NbaOracleRepoRoot
$cloudflared = Get-NbaOracleCloudflaredPath
$port = Get-NbaOracleApiPort

Set-Location $repoRoot
Write-Host "Starting NBA Oracle Cloudflare tunnel on http://127.0.0.1:$port"

& $cloudflared "tunnel" "--protocol" "http2" "--url" "http://127.0.0.1:$port"
