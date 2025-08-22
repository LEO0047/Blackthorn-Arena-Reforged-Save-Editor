@echo off
REM 需要先安裝 PyInstaller： pip install pyinstaller
pyinstaller --onefile --windowed src\blackthorn_arena_reforged_save_editor_zh.py
echo.
echo Build 完成，檔案在 dist\ 內。
pause
