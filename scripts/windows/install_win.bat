@echo off
setlocal EnableExtensions EnableDelayedExpansion


set "LICENSE_FILE=LICENSE"

set "PYTHON_DIR=python_embedded"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"
set "GET_PIP=%PYTHON_DIR%\get-pip.py"
set "VENV_DIR=v_FcsIT_env"
set "LAUNCHER_BAT=%~dp0FcsIT.bat"

set "PTU_CORR_DIR=src\Methods\PTU_Corr"
set "THIRD_PARTY_DIR=src\Methods\PTU_Corr\include\Third_party"

:: Default: do NOT download third-party component unless user explicitly agrees
set "FCSIT_DOWNLOAD_READPTU_FLIM=0"

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
:: 2) Prompt for readPTU_FLIM.py download (MIT)
:: ------------------------------------------------------------

echo.
echo The PTU_Corr module requires a third-party component:
echo   - readPTU_FLIM.py (MIT License), downloaded from an external repository during installation.
echo.
echo If you accept, the installer will download readPTU_FLIM.py and store it together with
echo the MIT license text in:
echo   %THIRD_PARTY_DIR%
echo.
echo If you deny, the PTU_Corr module directory will be removed and PTU_Corr functionality will NOT be installed.
echo.

choice /c YN /n /m "Download and install readPTU_FLIM.py now? [y/n]: "
if errorlevel 2 goto READPTU_NO
if errorlevel 1 goto READPTU_YES
goto READPTU_PROMPT

:READPTU_YES
set "FCSIT_DOWNLOAD_READPTU_FLIM=1"
echo Accepted. readPTU_FLIM.py will be downloaded during installation.
goto AFTER_READPTU

:READPTU_NO
set "FCSIT_DOWNLOAD_READPTU_FLIM=0"
echo Denied. Proceeding with partial installation (without PTU_Corr).
if exist "%PTU_CORR_DIR%" (
    echo Removing module directory: %PTU_CORR_DIR%
    rmdir /s /q "%PTU_CORR_DIR%"
    if exist "%PTU_CORR_DIR%" (
        echo ERROR: Failed to remove %PTU_CORR_DIR%. Exiting.
        exit /b 1
    )
)
goto AFTER_READPTU

:READPTU_PROMPT
goto AFTER_READPTU

:AFTER_READPTU

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

:: Ensure setup.py sees the flag (child processes inherit environment)
set "FCSIT_DOWNLOAD_READPTU_FLIM=%FCSIT_DOWNLOAD_READPTU_FLIM%"

"%~dp0%VENV_DIR%\Scripts\pip.exe" install . --no-warn-script-location --disable-pip-version-check --verbose >install.log 2>&1
if errorlevel 1 (
    echo Failed to install dependencies. Exiting.
    exit /b 1
)

:: Create the launcher .bat file
echo Creating the FcsIT.bat file...
echo @echo off > "%LAUNCHER_BAT%"
echo call "%~dp0%VENV_DIR%\Scripts\activate.bat" >> "%LAUNCHER_BAT%"
echo cd /d "%~dp0FcsIT" >> "%LAUNCHER_BAT%"
echo. >> "%LAUNCHER_BAT%"
echo :: Remove 'rem' below to enable functions' timing >> "%LAUNCHER_BAT%"
echo rem python FcsIT.py --timing >> "%LAUNCHER_BAT%"
echo. >> "%LAUNCHER_BAT%"
echo :: If timing enabled above, add 'rem' before the line below to avoid duplicate execution >> "%LAUNCHER_BAT%"
echo python FcsIT.py >> "%LAUNCHER_BAT%"
echo. >> "%LAUNCHER_BAT%"
echo call "%~dp0%VENV_DIR%\Scripts\deactivate.bat" >> "%LAUNCHER_BAT%"

if errorlevel 1 (
    echo Failed to create launcher .bat file. Exiting.
    exit /b 1
)

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
    if /I not "%%f"=="install_win.bat" if /I not "%%f"=="setup.py" if /I not "%%f"=="FcsIT.bat" if /I not "%%f"=="FcsIT" if /I not "%%f"=="%VENV_DIR%" if /I not "%%f"=="%PYTHON_DIR%" (
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
pause

endlocal
