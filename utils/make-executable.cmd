@echo off
set PYTHON=.\Scripts\python
set PYINSTALLER=.\Scripts\pyinstaller.exe

cd ..

%PYTHON% -c "exec('import sys\nif sys.base_prefix != sys.prefix:\n    sys.exit(0)\nelse:    sys.exit(1)')"
if ERRORLEVEL 1 (
	echo Error! You must run this script in the virtual environment.
	exit 1
)

%PYINSTALLER% -F --paths ./Lib/site-packages ./src/esync.py