param(
    [int]$IntervalMinutes = 30,
    [switch]$DryRun
)

. (Join-Path $PSScriptRoot "nba_oracle_common.ps1")

if ($IntervalMinutes -lt 30) {
    throw "interval_must_be_at_least_30_minutes"
}

$repoRoot = Get-NbaOracleRepoRoot
$taskName = Get-NbaOracleSchedulerTaskName
$runnerScript = Join-Path $repoRoot "scripts\run_nba_oracle_scheduler.ps1"
$powershellExe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not (Test-Path $runnerScript)) {
    throw "scheduler_runner_script_missing"
}

$escapedTaskCommand = '"' + $powershellExe + '" -NoProfile -ExecutionPolicy Bypass -File "' + $runnerScript + '"'

Write-Host "Registering scheduled task '$taskName' to run every $IntervalMinutes minutes."

$arguments = @(
    "/Create",
    "/F",
    "/SC", "MINUTE",
    "/MO", "$IntervalMinutes",
    "/TN", $taskName,
    "/TR", $escapedTaskCommand
)

if ($DryRun) {
    Write-Host "Dry run only."
    Write-Host ("schtasks.exe " + ($arguments -join " "))
    exit 0
}

& schtasks.exe @arguments

if ($LASTEXITCODE -ne 0) {
    throw "scheduled_task_registration_failed"
}

Write-Host "Scheduled task registered."
Write-Host "Verify with: schtasks /Query /TN `"$taskName`" /V /FO LIST"
