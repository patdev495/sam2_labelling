@echo off
cd /d "%~dp0"
uv run python -m auto_labelling.main
pause
