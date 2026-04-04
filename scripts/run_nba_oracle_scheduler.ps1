param(
    [switch]$DryRun
)

. (Join-Path $PSScriptRoot "nba_oracle_common.ps1")

$repoRoot = Get-NbaOracleRepoRoot
$pythonInvocation = Get-NbaOraclePythonInvocation
$logPath = Get-NbaOracleSchedulerLogPath
$timestamp = (Get-Date).ToString("s")

if ($DryRun) {
    Write-Host "Repo root: $repoRoot"
    Write-Host "Scheduler log: $logPath"
    Write-Host "Python invocation: $($pythonInvocation.Executable) $($pythonInvocation.Arguments -join ' ') main.py run-scheduler-once"
    exit 0
}

Add-Content -Path $logPath -Value "=== [$timestamp] NBA Oracle scheduler task starting ==="

Push-Location $repoRoot
try {
    $output = Invoke-NbaOraclePython -Arguments @("main.py", "run-scheduler-once") 2>&1
    $outputText = $output | Out-String
    if ($outputText.Trim()) {
        Add-Content -Path $logPath -Value $outputText.TrimEnd()
    }

    if ($LASTEXITCODE -ne 0) {
        throw "scheduler_run_failed_exit_code_$LASTEXITCODE"
    }

    Add-Content -Path $logPath -Value "=== [$timestamp] NBA Oracle scheduler task completed ==="
}
catch {
    Add-Content -Path $logPath -Value "=== [$timestamp] NBA Oracle scheduler task failed: $($_.Exception.Message) ==="
    throw
}
finally {
    Pop-Location
}
