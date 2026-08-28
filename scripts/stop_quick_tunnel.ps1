$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimePath = Join-Path $projectRoot "_working\quick-tunnel\runtime.json"

if (-not (Test-Path -LiteralPath $runtimePath)) {
    Write-Host "No FileMate quick tunnel runtime was recorded."
    exit 0
}

$runtime = Get-Content -Raw -LiteralPath $runtimePath | ConvertFrom-Json
foreach ($processId in @($runtime.cloudflared_pid, $runtime.gateway_pid, $runtime.backend_pid)) {
    if (-not $processId) {
        continue
    }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" `
        -ErrorAction SilentlyContinue
    if (-not $process) {
        continue
    }
    $commandLine = [string]$process.CommandLine
    $isFileMateProcess = `
        ($processId -eq $runtime.backend_pid -and $commandLine.Contains("server.py")) -or `
        ($processId -eq $runtime.gateway_pid -and $commandLine.Contains("demo_gateway.mjs")) -or `
        ($processId -eq $runtime.cloudflared_pid -and $commandLine.Contains("127.0.0.1:8080"))
    if ($isFileMateProcess) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

foreach ($port in @(8010, 8080)) {
    $listeners = Get-NetTCPConnection -LocalPort $port -State Listen `
        -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        $owner = Get-CimInstance Win32_Process `
            -Filter "ProcessId = $($listener.OwningProcess)" `
            -ErrorAction SilentlyContinue
        if (-not $owner) {
            continue
        }
        $commandLine = [string]$owner.CommandLine
        $isExpectedListener = `
            ($port -eq 8010 -and $commandLine.Contains("server.py")) -or `
            ($port -eq 8080 -and $commandLine.Contains("demo_gateway.mjs"))
        if ($isExpectedListener) {
            Stop-Process -Id $owner.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

Remove-Item -LiteralPath $runtimePath -Force
Write-Host "FileMate quick tunnel stopped."
