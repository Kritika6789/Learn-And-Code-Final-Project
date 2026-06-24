@echo off
echo Starting PRM Server...

:: Uncomment and fill these in to enable the Gmail SMTP integration
:: set SMTP_USER=your-email@gmail.com
:: set SMTP_PASSWORD=your-16-character-app-password

:: Navigate to the directory containing this script, then start the server
cd /d "%~dp0"
uvicorn server.main:app --reload
pause
