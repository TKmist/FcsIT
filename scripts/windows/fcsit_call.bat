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
rem Run the PowerShell FcsIT TCP/JSON client from cmd.exe.

setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0fcsit_call.ps1" %*
set "FCSIT_CALL_EXIT=%ERRORLEVEL%"
endlocal & exit /b %FCSIT_CALL_EXIT%
