@echo off
REM Activate virtualenv if present
if exist "%~dp0.venv\Scripts\activate.bat" (
  call "%~dp0.venv\Scripts\activate.bat"
  
)

python "%~dp0src\main.py"
