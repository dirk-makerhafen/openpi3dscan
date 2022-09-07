pyinstaller --onefile -F --clean  rc_rebase.py
pyinstaller --onefile -F --clean  process.py
IF %ERRORLEVEL% NEQ 0 PAUSE