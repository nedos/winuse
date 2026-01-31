param(
    [string]$Path = "C:\\winuse",
    [string]$HostAddr = "0.0.0.0",
    [int]$Port = 8080
)

Set-Location $Path
$env:WINUSE_API_HOST = $HostAddr
$env:WINUSE_API_PORT = $Port
$env:WINUSE_FAILSAFE = "false"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python not found in PATH"
    exit 1
}

$logPathOut = Join-Path $Path "winuse.out.log"
$logPathErr = Join-Path $Path "winuse.err.log"

# Start WinUse in background without blocking the SSH session
Start-Process -WindowStyle Hidden -FilePath "python" `
    -ArgumentList "-m", "winuse" `
    -WorkingDirectory $Path `
    -RedirectStandardOutput $logPathOut `
    -RedirectStandardError $logPathErr

Write-Output "WinUse started on ${HostAddr}:${Port} (log: $logPathOut)"
