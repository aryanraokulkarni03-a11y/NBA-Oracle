Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-NbaOracleRepoRoot {
    return [string](Resolve-Path (Join-Path $PSScriptRoot ".."))
}

function Get-NbaOracleEnvMap {
    $repoRoot = Get-NbaOracleRepoRoot
    $envPath = Join-Path $repoRoot ".env"
    $values = @{}
    if (-not (Test-Path $envPath)) {
        return $values
    }

    foreach ($line in Get-Content $envPath) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        $parts = $trimmed -split "=", 2
        if ($parts.Length -ne 2) {
            continue
        }
        $values[$parts[0].Trim()] = $parts[1].Trim()
    }

    return $values
}

function Get-NbaOracleEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [string]$Default = ""
    )

    $values = Get-NbaOracleEnvMap
    if ($values.ContainsKey($Name) -and $values[$Name]) {
        return $values[$Name]
    }
    return $Default
}

function Get-NbaOracleApiPort {
    $raw = Get-NbaOracleEnvValue -Name "ORACLE_API_PORT" -Default "8000"
    if (-not $raw) {
        return 8000
    }
    return [int]$raw
}

function Get-NbaOraclePythonInvocation {
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) {
        return @{
            Executable = $python.Source
            Arguments = @()
        }
    }

    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        return @{
            Executable = $py.Source
            Arguments = @("-3")
        }
    }

    throw "python_not_found"
}

function Invoke-NbaOraclePython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $pythonInvocation = Get-NbaOraclePythonInvocation
    $allArguments = @()
    $allArguments += $pythonInvocation.Arguments
    $allArguments += $Arguments
    & $pythonInvocation.Executable @allArguments
}

function Get-NbaOracleCloudflaredPath {
    $candidates = @()

    $cloudflared = Get-Command cloudflared.exe -ErrorAction SilentlyContinue
    if ($cloudflared) {
        $candidates += $cloudflared.Source
    }

    $cloudflaredBare = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($cloudflaredBare) {
        $candidates += $cloudflaredBare.Source
    }

    $programFiles = ${env:ProgramFiles}
    $programFilesX86 = ${env:ProgramFiles(x86)}
    if ($programFiles) {
        $candidates += (Join-Path $programFiles "cloudflared\cloudflared.exe")
    }
    if ($programFilesX86) {
        $candidates += (Join-Path $programFilesX86 "cloudflared\cloudflared.exe")
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    throw "cloudflared_not_found"
}

function Get-NbaOracleSchedulerTaskName {
    return "NBA Oracle Scheduler"
}

function Get-NbaOracleSchedulerLogPath {
    $repoRoot = Get-NbaOracleRepoRoot
    $runtimeStateDir = Join-Path $repoRoot "data\runtime_state"
    New-Item -ItemType Directory -Path $runtimeStateDir -Force | Out-Null
    return (Join-Path $runtimeStateDir "phase6_scheduler_task.log")
}
