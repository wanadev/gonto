:: Make and/or activate the virtualenv
IF NOT EXIST build\__env__ (
    mkdir build
    python3.13 -m venv build\__env__
)
CALL build\__env__\Scripts\activate.bat

:: Install compilation tools (Nuitka,...)
pip install -r winbuild\requirements.txt

:: Install Python dependencies.
pip install .

:: Compile with nuitka
python -m nuitka ^
    --mode=standalone ^
    --follow-imports ^
    --python-flag=-O,isolated ^
    --assume-yes-for-downloads ^
    --windows-console-mode=force ^
    --windows-uac-admin ^
    --windows-icon-from-ico=winbuild\gonto.ico ^
    --output-filename=gonto.exe ^
    winbuild\gonto-win.py

:: Copy additional files...
copy LICENSE.txt gonto-win.dist\LICENSE.txt

:: Leave the virtualenv
deactivate
