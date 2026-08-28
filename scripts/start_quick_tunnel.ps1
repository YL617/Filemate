param(
    [string]$Username = "filemate",
    [string]$Password = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$workingDir = Join-Path $projectRoot "_working\quick-tunnel"
$toolDir = Join-Path $workingDir "tools"
$dataDir = Join-Path $workingDir "data"
$distIndex = Join-Path $projectRoot "filemate\web\dist\index.html"
$cloudflaredPath = Join-Path $toolDir "cloudflared.exe"
$runtimePath = Join-Path $workingDir "runtime.json"
$credentialsPath = Join-Path $workingDir "credentials.json"
$backendLog = Join-Path $workingDir "backend.stdout.log"
$backendErrorLog = Join-Path $workingDir "backend.stderr.log"
$gatewayLog = Join-Path $workingDir "gateway.stdout.log"
$gatewayErrorLog = Join-Path $workingDir "gateway.stderr.log"
$tunnelLog = Join-Path $workingDir "tunnel.stdout.log"
$tunnelErrorLog = Join-Path $workingDir "tunnel.stderr.log"

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $result = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $result.AsyncWaitHandle.WaitOne(300)) {
            return $false
        }
        $client.EndConnect($result)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

function Wait-LocalUrl([string]$Uri, [hashtable]$Headers, [int]$Seconds = 30) {
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            return Invoke-WebRequest -Uri $Uri -Headers $Headers `
                -TimeoutSec 3 -UseBasicParsing
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    throw "Timed out waiting for $Uri"
}

New-Item -ItemType Directory -Force -Path $workingDir, $toolDir, $dataDir | Out-Null
if (Test-Path -LiteralPath $runtimePath) {
    & (Join-Path $PSScriptRoot "stop_quick_tunnel.ps1")
}
if ((Test-LocalPort 8010) -or (Test-LocalPort 8080)) {
    throw "Port 8010 or 8080 is already in use. Refusing to stop an unverified process."
}
if (-not (Test-Path -LiteralPath $distIndex)) {
    throw "Vue production build is missing. Run npm run build in filemate/web first."
}

if (-not $Password -and (Test-Path -LiteralPath $credentialsPath)) {
    $savedCredentials = Get-Content -Raw -LiteralPath $credentialsPath | ConvertFrom-Json
    $Username = [string]$savedCredentials.username
    $Password = [string]$savedCredentials.password
}
if (-not $Password) {
    $randomBytes = [byte[]]::new(15)
    $randomGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $randomGenerator.GetBytes($randomBytes)
    } finally {
        $randomGenerator.Dispose()
    }
    $Password = [Convert]::ToBase64String($randomBytes).TrimEnd("=").Replace("+", "A").Replace("/", "B")
}

if (-not (Test-Path -LiteralPath $cloudflaredPath)) {
    Write-Host "Downloading official cloudflared..."
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $cloudflaredPath -UseBasicParsing
    Unblock-File -LiteralPath $cloudflaredPath -ErrorAction SilentlyContinue
}

$uvPath = (Get-Command uv -ErrorAction Stop).Source
$nodePath = (Get-Command node -ErrorAction Stop).Source
$previousEnvironment = @{}
$backendEnvironment = @{
    FILEMATE_HOST = "127.0.0.1"
    FILEMATE_PORT = "8010"
    FILEMATE_DATA_DIR = $dataDir
    FILEMATE_DB_PATH = (Join-Path $dataDir "filemate.db")
    FILEMATE_UPLOAD_DIR = (Join-Path $dataDir "inbox")
    FILEMATE_ARCHIVE_DIR = (Join-Path $dataDir "archive")
}

try {
    foreach ($name in $backendEnvironment.Keys) {
        $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        [Environment]::SetEnvironmentVariable($name, $backendEnvironment[$name], "Process")
    }
    $backend = Start-Process -FilePath $uvPath `
        -ArgumentList @("run", "python", "server.py") `
        -WorkingDirectory $projectRoot -WindowStyle Hidden `
        -RedirectStandardOutput $backendLog -RedirectStandardError $backendErrorLog `
        -PassThru
} finally {
    foreach ($name in $backendEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
    }
}

try {
    Wait-LocalUrl "http://127.0.0.1:8010/api/health" @{} | Out-Null

    $gatewayEnvironment = @{
        FILEMATE_GATEWAY_PORT = "8080"
        FILEMATE_GATEWAY_BACKEND = "http://127.0.0.1:8010"
        FILEMATE_WEB_DIST = (Join-Path $projectRoot "filemate\web\dist")
        FILEMATE_BASIC_USER = $Username
        FILEMATE_BASIC_PASSWORD = $Password
    }
    foreach ($name in $gatewayEnvironment.Keys) {
        $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        [Environment]::SetEnvironmentVariable($name, $gatewayEnvironment[$name], "Process")
    }
    try {
        $gateway = Start-Process -FilePath $nodePath `
            -ArgumentList @("scripts/demo_gateway.mjs") `
            -WorkingDirectory $projectRoot -WindowStyle Hidden `
            -RedirectStandardOutput $gatewayLog -RedirectStandardError $gatewayErrorLog `
            -PassThru
    } finally {
        foreach ($name in $gatewayEnvironment.Keys) {
            [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
        }
    }

    $basicValue = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("$Username`:$Password"))
    $headers = @{ Authorization = "Basic $basicValue" }
    Wait-LocalUrl "http://127.0.0.1:8080/" $headers | Out-Null
    $backendListener = Get-NetTCPConnection -LocalPort 8010 -State Listen `
        -ErrorAction Stop | Select-Object -First 1

    $cloudflared = Start-Process -FilePath $cloudflaredPath `
        -ArgumentList @("tunnel", "--url", "http://127.0.0.1:8080", "--protocol", "http2", "--no-autoupdate") `
        -WorkingDirectory $projectRoot -WindowStyle Hidden `
        -RedirectStandardOutput $tunnelLog -RedirectStandardError $tunnelErrorLog `
        -PassThru

    $deadline = (Get-Date).AddSeconds(75)
    $publicUrl = ""
    $registered = $false
    while ((Get-Date) -lt $deadline -and (-not $publicUrl -or -not $registered)) {
        Start-Sleep -Milliseconds 500
        $combinedLog = ""
        if (Test-Path -LiteralPath $tunnelLog) {
            $combinedLog += Get-Content -Raw -LiteralPath $tunnelLog -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $tunnelErrorLog) {
            $combinedLog += Get-Content -Raw -LiteralPath $tunnelErrorLog -ErrorAction SilentlyContinue
        }
        $match = [regex]::Match($combinedLog, "https://[a-z0-9-]+\.trycloudflare\.com")
        if ($match.Success) {
            $publicUrl = $match.Value
        }
        $registered = $combinedLog.Contains("Registered tunnel connection")
        $cloudflared.Refresh()
        if ($cloudflared.HasExited) {
            throw "cloudflared exited before assigning a URL. Check $tunnelErrorLog"
        }
    }
    if (-not $publicUrl) {
        throw "Cloudflare did not assign a quick tunnel URL within 75 seconds."
    }
    if (-not $registered) {
        throw "Cloudflare assigned a URL but did not register an edge connection within 75 seconds."
    }

    [ordered]@{
        schema_version = 1
        started_at = (Get-Date).ToUniversalTime().ToString("o")
        public_url = $publicUrl
        backend_pid = $backendListener.OwningProcess
        gateway_pid = $gateway.Id
        cloudflared_pid = $cloudflared.Id
    } | ConvertTo-Json | Set-Content -LiteralPath $runtimePath -Encoding utf8
    [ordered]@{
        username = $Username
        password = $Password
    } | ConvertTo-Json | Set-Content -LiteralPath $credentialsPath -Encoding utf8

    Write-Host "FileMate quick tunnel is ready."
    Write-Host "URL: $publicUrl"
    Write-Host "Username: $Username"
    Write-Host "Password: $Password"
    Write-Host "Keep this computer awake. Stop with scripts/stop_quick_tunnel.ps1"
} catch {
    foreach ($candidate in @($cloudflared, $gateway, $backend)) {
        if ($candidate) {
            Stop-Process -Id $candidate.Id -Force -ErrorAction SilentlyContinue
        }
    }
    foreach ($port in @(8010, 8080)) {
        $listeners = Get-NetTCPConnection -LocalPort $port -State Listen `
            -ErrorAction SilentlyContinue
        foreach ($listener in $listeners) {
            $owner = Get-CimInstance Win32_Process `
                -Filter "ProcessId = $($listener.OwningProcess)" `
                -ErrorAction SilentlyContinue
            $commandLine = if ($owner) { [string]$owner.CommandLine } else { "" }
            $isExpectedListener = `
                ($port -eq 8010 -and $commandLine.Contains("server.py")) -or `
                ($port -eq 8080 -and $commandLine.Contains("demo_gateway.mjs"))
            if ($owner -and $isExpectedListener) {
                Stop-Process -Id $owner.ProcessId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    throw
}
