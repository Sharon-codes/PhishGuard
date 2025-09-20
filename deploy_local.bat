@echo off
echo Starting PhishGuard Application...

REM Start backend
echo Starting Flask backend...
cd backend
start /B python app.py

REM Wait a moment for backend to start
timeout /t 5 /nobreak

REM Start frontend
echo Starting React frontend...
cd ../frontend
start /B npm run dev

echo PhishGuard is starting up...
echo Backend: http://localhost:5001
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop both servers...
pause

REM Kill the processes
taskkill /f /im node.exe
taskkill /f /im python.exe
