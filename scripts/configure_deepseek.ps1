param(
    [string]$EnvPath = (Join-Path $PSScriptRoot "..\.env")
)

$ErrorActionPreference = "Stop"
$targetPath = [System.IO.Path]::GetFullPath($EnvPath)
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if (-not $targetPath.StartsWith($projectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "EnvPath 必须位于 FileMate 项目目录内"
}

$secureKey = Read-Host "请输入 DeepSeek API Key（输入不会显示）" -AsSecureString
$keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        throw "DeepSeek API Key 不能为空"
    }

    $existingLines = if (Test-Path -LiteralPath $targetPath) {
        Get-Content -LiteralPath $targetPath
    } else {
        @()
    }
    $managedPattern = '^\s*(LLM_PROVIDER|LLM_API_KEY|LLM_BASE_URL|LLM_MODEL)\s*='
    $preservedLines = @($existingLines | Where-Object { $_ -notmatch $managedPattern })
    $managedLines = @(
        "LLM_PROVIDER=deepseek"
        "LLM_API_KEY=$apiKey"
        "LLM_BASE_URL=https://api.deepseek.com"
        "LLM_MODEL=deepseek-v4-flash"
    )
    $outputLines = @($preservedLines) + @("", "# DeepSeek V4 Flash") + $managedLines
    Set-Content -LiteralPath $targetPath -Value $outputLines -Encoding utf8
    Write-Host "DeepSeek V4 Flash 配置已写入 $targetPath" -ForegroundColor Green
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
}
