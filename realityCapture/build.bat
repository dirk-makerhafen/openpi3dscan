pyinstaller --onefile -F --clean -w rc_rebase.py
pyinstaller --onefile -F --clean -w process.py
IF %ERRORLEVEL% NEQ 0 PAUSE