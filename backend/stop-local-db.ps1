$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\python.exe -c "from pathlib import Path; import pymysql; p=Path('.local/mysql-root-password.txt').read_text().strip(); c=pymysql.connect(host='127.0.0.1',port=3307,user='root',password=p); c.cursor().execute('SHUTDOWN'); c.close()"
