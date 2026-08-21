@echo off
rem Copyright (C) 2026 TKmist (https://github.com/TKmist)
rem
rem This file is part of the FcsIT repository.
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU General Public License as published by
rem the Free Software Foundation, either version 3 of the License, or any later version.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
rem FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License along with
rem this program. If not, see https://www.gnu.org/licenses/.
rem Send one FcsIT TCP/JSON command using the bundled Python runtime.

setlocal EnableExtensions
set "FCSIT_PYTHON=%~dp0v_FcsIT_env\Scripts\python.exe"
set "FCSIT_CLIENT=%~dp0FcsIT\include\tcp_client.py"

if not exist "%FCSIT_PYTHON%" set "FCSIT_PYTHON=%~dp0python_embedded\python.exe"
if not exist "%FCSIT_CLIENT%" set "FCSIT_CLIENT=%~dp0src\include\tcp_client.py"

if not exist "%FCSIT_PYTHON%" (
    echo FcsIT Python runtime not found. Run install_win.bat first. 1>&2
    exit /b 1
)
if not exist "%FCSIT_CLIENT%" (
    echo FcsIT TCP/JSON client module not found. 1>&2
    exit /b 1
)

"%FCSIT_PYTHON%" "%FCSIT_CLIENT%" %*
set "FCSIT_CALL_EXIT=%ERRORLEVEL%"
endlocal & exit /b %FCSIT_CALL_EXIT%
