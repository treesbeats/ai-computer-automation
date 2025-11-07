@echo off
REM Build a Windows installer (VoiceAssistantSetup.exe) for the dashboard experience.
setlocal

set ROOT=%~dp0..
set APP_NAME=VoiceAssistantDashboard

if not defined PYTHON (
    set PYTHON=py
)

echo === Installing build dependencies ===
%PYTHON% -m pip install .[build]

echo === Creating standalone dashboard executable with PyInstaller ===
%PYTHON% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name %APP_NAME% ^
    --windowed ^
    --add-data "%ROOT%\examples\config.sample.json;examples" ^
    "%ROOT%\src\voice_assistant\dashboard_app.py"

if errorlevel 1 (
    echo PyInstaller build failed.
    exit /b 1
)

set INNO_SETUP_EXE=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set INNO_SETUP_EXE="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set INNO_SETUP_EXE="%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined INNO_SETUP_EXE (
    echo Could not find Inno Setup compiler (ISCC.exe). Install Inno Setup 6 and re-run this script.
    exit /b 1
)

echo === Packaging installer with Inno Setup ===
%INNO_SETUP_EXE% /DAppVersion=1.0.0 "%ROOT%\installer\voice_assistant.iss"

if errorlevel 1 (
    echo Inno Setup packaging failed.
    exit /b 1
)

echo === Done ===
echo Output installer: %ROOT%\installer\Output\VoiceAssistantSetup.exe

endlocal
