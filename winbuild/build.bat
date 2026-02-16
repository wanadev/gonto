:: Make and/or activate the virtualenv
IF NOT EXIST build\__env__ (
    mkdir build
    python -m venv build\__env__
)
CALL build\__env__\Scripts\activate.bat

:: Install compilation tools (Nuitka,...)
pip install -r winbuild\requirements.txt

:: Install Python dependencies.
pip install .

:: Compile with nuitka
python -m nuitka ^
    --follow-imports ^
    --assume-yes-for-downloads ^
    --windows-console-mode=attach ^
    --windows-uac-admin ^
    --windows-icon-from-ico=winbuild\gonto.ico ^
    --standalone ^
    winbuild\gonto-win.py

:: Copy additional files...
copy LICENSE.txt gonto-win.dist\LICENSE.txt

:: Leave the virtualenv
deactivate
