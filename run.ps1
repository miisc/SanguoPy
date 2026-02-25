Set-Location -Path $PSScriptRoot
if (Test-Path ".venv\Scripts\Activate.ps1") {
  . ".venv\Scripts\Activate.ps1"
}
python .\src\main.py
