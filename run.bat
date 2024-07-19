@echo off
set "PROJECT_DIR=%WATCH_PB_PROJECT_DIR%"
cd /d "%PROJECT_DIR%"
"%PROJECT_DIR%\.venv\Scripts\python.exe" main.py
