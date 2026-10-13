@echo off
title Mutual Fund Portfolio Manager
echo =========================================
echo Starting Mutual Fund Portfolio App...
echo =========================================

cd /d "%~dp0"

:: Start the Flask server in the background
start /B .\venv\Scripts\python.exe app.py

:: Wait a few seconds for the server to start
timeout /t 3 /nobreak >nul

:: Open it in the default browser
start http://127.0.0.1:5000

echo Application is running in your browser!
echo Do not close this black window until you are finished using the app.
