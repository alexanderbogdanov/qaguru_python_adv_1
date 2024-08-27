@echo off
taskkill /F /IM python.exe /T


REM Run the Batch File After Stopping the Service:
REM uvicorn main:app --host 127.0.0.1 --port 8000
REM # After stopping the service
REM .\kill_python_processes.bat