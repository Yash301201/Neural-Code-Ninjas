param([ValidateRange(1, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$mysqlBinary = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$databaseDirectory = Join-Path $PSScriptRoot '.local\mysql-data'
if (!(Test-Path -LiteralPath $projectPython)) { throw 'Create .venv and install requirements first. See README.md.' }
if (!(Test-Path -LiteralPath $databaseDirectory)) { throw 'Local database missing. Follow manual MySQL setup in README.md.' }
$apiUrl = "http://127.0.0.1:$Port"
$portOccupied = & $projectPython -c "import socket; s=socket.socket(); s.settimeout(1); print(s.connect_ex(('127.0.0.1',$Port))==0); s.close()"
if ($portOccupied -eq 'True') {
    $existingProject = $false
    try {
        $contract = Invoke-RestMethod -Uri "$apiUrl/openapi.json" -TimeoutSec 5
        $health = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 5
        $existingProject = ($contract.info.title -eq 'LearnPath AI Backend' -and $health.status -eq 'ok' -and $health.database -eq 'connected')
    } catch {
        $existingProject = $false
    }
    if ($existingProject) {
        Write-Host "LearnPath AI is already running and its database is connected."
        Write-Host "Frontend: $apiUrl/app/"
        Write-Host "Swagger: $apiUrl/docs"
        Write-Host 'Local admin login: .local/admin-login.txt'
        exit 0
    }
    throw "Port $Port is occupied by another or unhealthy server. Start on another port: powershell -ExecutionPolicy Bypass -File .\start-local.ps1 -Port 8001"
}
$databaseRunning = & $projectPython -c "import socket; s=socket.socket(); s.settimeout(1); print(s.connect_ex(('127.0.0.1',3307))==0); s.close()"
if ($databaseRunning -ne 'True') {
    $mysqlArguments = @('--no-defaults', ('--basedir="' + (Split-Path (Split-Path $mysqlBinary)) + '"'), ('--datadir="' + $databaseDirectory + '"'), '--bind-address=127.0.0.1', '--port=3307', '--mysqlx=OFF')
    Start-Process -FilePath $mysqlBinary -ArgumentList $mysqlArguments -WindowStyle Hidden | Out-Null
    & $projectPython -c "import socket,time; ready=False; [time.sleep(.5) for _ in range(40) if not ready and not (ready := socket.socket().connect_ex(('127.0.0.1',3307)) == 0)]; raise SystemExit(0 if ready else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'MySQL did not start. Check .local/mysql-data/*.err.' }
}
Write-Host "Swagger: $apiUrl/docs"
Write-Host 'Local admin login: .local/admin-login.txt'
& $projectPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port
