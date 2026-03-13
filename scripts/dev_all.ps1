$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$frontendCommand = "Set-Location '$projectRoot'; pnpm dev:frontend"
$backendCommand = "Set-Location '$projectRoot'; pnpm dev:backend"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand -WorkingDirectory $projectRoot
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand -WorkingDirectory $projectRoot

Write-Output "Started backend on http://127.0.0.1:8000 and frontend on http://127.0.0.1:3000"
