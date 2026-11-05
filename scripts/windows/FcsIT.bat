@echo off
rem Run FcsIT with its local TCP/JSON command server enabled.

setlocal
cd /d "%~dp0FcsIT"
"%~dp0v_FcsIT_env\Scripts\python.exe" FcsIT.py --tcp-server %*
endlocal
