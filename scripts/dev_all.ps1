$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$frontendCommand = "Set-Location '$projectRoot'; pnpm dev:frontend"
$backendCommand = "Set-Location '$projectRoot'; pnpm dev:backend"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand -WorkingDirectory $projectRoot
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand -WorkingDirectory $projectRoot

Write-Output "Started backend on http://0.0.0.0:8000 and frontend on http://0.0.0.0:3000"
Write-Output "Tablets on the same network can connect through your PC IP, for example http://192.168.x.x:3000"
