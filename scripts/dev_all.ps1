$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$frontendCommand = "Set-Location '$projectRoot'; pnpm dev:frontend"
$backendCommand = "Set-Location '$projectRoot'; pnpm dev:backend"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand -WorkingDirectory $projectRoot
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand -WorkingDirectory $projectRoot

Write-Output "Started backend on http://0.0.0.0:8000 and frontend on http://127.0.0.1:3000"
Write-Output "Backend is now listening on 0.0.0.0:8000, so tablets on the same network can connect through your PC IP."
