@echo off
cd /d "%~dp0"
echo Alte EXE wird beendet...
taskkill /f /im AutoClicker.exe 2>nul
timeout /t 1 /nobreak >nul
pip install pynput pyinstaller pillow
python create_ico.py
pyinstaller --onefile --windowed --name AutoClicker --icon icon.ico --add-data "icon.ico;." --add-data "icon.png;." autoclicker.py
pyinstaller --onefile --windowed --name update --icon icon.ico update_checker.py
echo.
echo Installer wird erstellt (falls Inno Setup installiert)...
set ISCC_PATH=
where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    set ISCC_PATH=ISCC.exe
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set ISCC_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)
if defined ISCC_PATH (
    %ISCC_PATH% installer.iss
    echo Installer liegt im installer\ Ordner.
) else (
    echo Inno Setup nicht gefunden. Installer uebersprungen.
    echo Installiere es von: https://jrsoftware.org/isinfo.php
)
echo.
echo Fertig! EXE: dist\AutoClicker.exe
if exist installer\ echo Installer: installer\AutoClicker_Setup.exe
pause
