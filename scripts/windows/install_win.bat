@echo off
setlocal EnableExtensions EnableDelayedExpansion


set "LICENSE_FILE=LICENSE"

set "PYTHON_DIR=python_embedded"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"
set "GET_PIP=%PYTHON_DIR%\get-pip.py"
set "VENV_DIR=v_FcsIT_env"
set "LAUNCHER_BAT=%~dp0FcsIT.bat"

:: ------------------------------------------------------------
:: 1) GPLv3+ license prompt
:: ------------------------------------------------------------

echo ------------------------------------------------------------
echo FcsIT installer
echo ------------------------------------------------------------
echo.

if not exist "%LICENSE_FILE%" (
    echo ERROR: LICENSE file not found in the current directory.
    echo Expected: %CD%\%LICENSE_FILE%
    exit /b 1
)

echo This installer will set up FcsIT and its dependencies.
echo FcsIT is licensed under the GNU GPL v3 or later.
echo.

:LICENSE_MENU
echo Choose an option:
echo   [a] Continue installation
echo   [s] Show GPL license text
echo   [d] Abort the installation
echo Choosing 'Abort' will only terminate the installer.
echo The source code remains available to you under the terms of the GNU GPL v3 or later.

choice /c ASD /n /m "Your choice [a/s/d]: "
if errorlevel 3 goto LICENSE_DENY
if errorlevel 2 goto LICENSE_SHOW
if errorlevel 1 goto LICENSE_ACCEPT
goto LICENSE_MENU

:LICENSE_SHOW
echo Displaying LICENSE...
echo ------------------------------------------------------------
more "%LICENSE_FILE%"
echo ------------------------------------------------------------
goto LICENSE_MENU

:LICENSE_DENY
echo Installation aborted.
exit /b 1

:LICENSE_ACCEPT
echo Continuing installation.

:: ------------------------------------------------------------
:: 3) DejaVu fonts notice
:: ------------------------------------------------------------

echo.
echo ------------------------------------------------------------
echo Third-party asset notice: DejaVu fonts
echo ------------------------------------------------------------
echo.
echo This software uses the DejaVu Sans Condensed font (DejaVu Fonts Project).
echo License information is embedded in the font file metadata (TTF).
echo.

choice /c C /n /m "Press [c] to continue installation: "
echo Continuing...



:: Ensure the embedded Python exists
if not exist "%PYTHON_EXE%" (
    echo Embedded Python not found at %PYTHON_EXE%. Exiting.
    exit /b 1
)

:: Ensure pip is installed
if not exist "%PIP_EXE%" (
    echo Pip not found. Installing pip... 
    "%PYTHON_EXE%" "%GET_PIP%" --no-warn-script-location
    if errorlevel 1 (
        echo Failed to install pip. Exiting.
        exit /b 1
    )
)

:: Install virtualenv
echo Installing virtualenv...
"%PYTHON_EXE%" -m pip install virtualenv --no-warn-script-location
if errorlevel 1 (
    echo Failed to install virtualenv. Exiting.
    exit /b 1
)

:: Remove the existing virtual environment if it exists
if exist "%VENV_DIR%" (
    echo Removing old virtual environment...
    rmdir /s /q "%VENV_DIR%"
    if exist "%VENV_DIR%" (
        echo Failed to remove old virtual environment. Exiting.
        exit /b 1
    )
    echo Old virtual environment removed.
)

:: Create virtual environment using virtualenv
echo Creating virtual environment in %VENV_DIR%...
"%PYTHON_EXE%" -m virtualenv "%~dp0%VENV_DIR%"
if errorlevel 1 (
    echo Failed to create virtual environment. Exiting.
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment...
call "%~dp0%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment. Exiting.
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
"%PIP_EXE%" cache purge
"%PYTHON_EXE%" -m pip install virtualenv --no-warn-script-location

"%~dp0%VENV_DIR%\Scripts\pip.exe" install . --no-warn-script-location --disable-pip-version-check --verbose
if errorlevel 1 (
    echo Failed to install dependencies. Exiting.
    exit /b 1
)

:: Create the launcher .bat file
echo Creating the FcsIT.bat file...
echo @echo off > "%LAUNCHER_BAT%"
echo rem Copyright (C) 2026 TKmist (https://github.com/TKmist) >> "%LAUNCHER_BAT%"
echo rem. >> "%LAUNCHER_BAT%"
echo rem This file is part of the FcsIT repository. >> "%LAUNCHER_BAT%"
echo rem. >> "%LAUNCHER_BAT%"
echo rem This program is free software: you can redistribute it and/or modify >> "%LAUNCHER_BAT%"
echo rem it under the terms of the GNU General Public License as published by >> "%LAUNCHER_BAT%"
echo rem the Free Software Foundation, either version 3 of the License, or any later version. >> "%LAUNCHER_BAT%"
echo rem. >> "%LAUNCHER_BAT%"
echo rem This program is distributed in the hope that it will be useful, >> "%LAUNCHER_BAT%"
echo rem but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS >> "%LAUNCHER_BAT%"
echo rem FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. >> "%LAUNCHER_BAT%"
echo rem. >> "%LAUNCHER_BAT%"
echo rem You should have received a copy of the GNU General Public License along with >> "%LAUNCHER_BAT%"
echo rem this program. If not, see https://www.gnu.org/licenses/. >> "%LAUNCHER_BAT%"
echo setlocal >> "%LAUNCHER_BAT%"
echo cd /d "%%~dp0FcsIT" >> "%LAUNCHER_BAT%"
echo "%%~dp0%VENV_DIR%\Scripts\python.exe" FcsIT.py --tcp-server %%* >> "%LAUNCHER_BAT%"
echo endlocal >> "%LAUNCHER_BAT%"

if errorlevel 1 (
    echo Failed to create launcher .bat file. Exiting.
    exit /b 1
)

:: Verify the CLI client distributed beside install_win.bat.
if not exist "%~dp0fcsit_call.bat" (
    echo FcsIT CLI client not found: "%~dp0fcsit_call.bat"
    exit /b 1
)
echo FcsIT CLI client verified next to "%LAUNCHER_BAT%".

echo Creating the Windows shortcut on the Desktop...
set "SHORTCUT_NAME=FcsIT.lnk"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\%SHORTCUT_NAME%"
set "ICON_PATH=%~dp0FcsIT\res\icons\FcsIT.ico"
set "TEMP_VBS=%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

:: Build VBScript file (no parentheses block)
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP_VBS%"
echo Set oLink = oWS.CreateShortcut("%SHORTCUT_PATH%") >> "%TEMP_VBS%"
echo oLink.TargetPath = "%LAUNCHER_BAT%" >> "%TEMP_VBS%"
echo oLink.IconLocation = "%ICON_PATH%" >> "%TEMP_VBS%"
echo oLink.Description = "Launch FcsIT Application" >> "%TEMP_VBS%"
echo oLink.Save >> "%TEMP_VBS%"

:: Verify the script exists
if not exist "%TEMP_VBS%" (
    echo Failed to create VBS script: "%TEMP_VBS%"
    exit /b 1
)

echo Creating shortcut on Desktop...
cscript /nologo "%TEMP_VBS%"
if errorlevel 1 (
    echo Failed to create shortcut. Exiting.
    del "%TEMP_VBS%"
    exit /b 1
)

del "%TEMP_VBS%"

if exist "%SHORTCUT_PATH%" (
    echo Shortcut created successfully at "%SHORTCUT_PATH%".
) else (
    echo Failed to create shortcut. Please check the script.
)


:: Deactivate the virtual environment
echo Deactivating virtual environment...
call "%~dp0%VENV_DIR%\Scripts\deactivate.bat"

:: Rename src directory to FcsIT
echo Renaming src directory to FcsIT...
rename src FcsIT
if errorlevel 1 (
    echo Failed to rename src directory to FcsIT. Exiting.
    exit /b 1
)

:: Move files to the FcsIT directory
echo Moving files to FcsIT directory...
for %%f in (*) do (
    if /I not "%%f"=="install_win.bat" if /I not "%%f"=="setup.py" if /I not "%%f"=="FcsIT.bat" if /I not "%%f"=="fcsit_call.bat" if /I not "%%f"=="FcsIT" if /I not "%%f"=="%VENV_DIR%" if /I not "%%f"=="%PYTHON_DIR%" (
        move "%%f" FcsIT\
        if errorlevel 1 (
            echo Failed to move file %%f to FcsIT directory. Exiting.
            exit /b 1
        )
    )
)

:: Remove setup.py and install_win.bat
echo Removing setup.py and install_win.bat...
del setup.py
del install_win.bat

echo Installation completed successfully!
echo The FcsIT TCP/JSON server is enabled in "%LAUNCHER_BAT%".
echo The FcsIT TCP/JSON CLI client is installed next to "%LAUNCHER_BAT%".
echo The server listens on localhost port 8765 by default.
pause

endlocal
