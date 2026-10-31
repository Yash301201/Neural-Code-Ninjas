param([ValidateRange(1, 65535)][int]$Port = 8001, [switch]$Rebuild)
$ErrorActionPreference = 'Stop'
$reactDirectory = Join-Path $PSScriptRoot 'frontend-react'
if ($Rebuild -or !(Test-Path -LiteralPath (Join-Path $reactDirectory 'dist\index.html'))) {
    Push-Location -LiteralPath $reactDirectory
    try {
        if (!(Test-Path -LiteralPath 'node_modules')) {
            & npm ci --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { throw 'React dependency installation failed.' }
        }
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw 'React build failed.' }
    } finally { Pop-Location }
}
Write-Host "LearnPath AI integrated React portal: http://127.0.0.1:$Port/app/"
Write-Host 'Four-role credentials: backend/.local/portal-logins.txt'
Set-Location -LiteralPath (Join-Path $PSScriptRoot 'backend')
& powershell -ExecutionPolicy Bypass -File .\start-local.ps1 -Port $Port
exit $LASTEXITCODE
