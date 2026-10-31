param([ValidateRange(1, 65535)][int]$Port = 8001, [switch]$Rebuild)
& (Join-Path (Split-Path $PSScriptRoot) 'start-project.ps1') -Port $Port -Rebuild:$Rebuild
exit $LASTEXITCODE
