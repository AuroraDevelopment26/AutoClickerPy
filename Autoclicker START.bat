@echo off
cd /d "%~dp0"
pip install -q pynput
python autoclicker.py
pause
