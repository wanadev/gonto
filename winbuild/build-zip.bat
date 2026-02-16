:: Get the PodoNex version
FOR /F %%i IN ('python -c "import tomllib;print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"') DO (
    SET VERSION=%%i
)

:: Output name
SET OUTPUT_NAME=gonto_%VERSION%_win64

:: Create required folders
mkdir build
mkdir dist

:: Release
xcopy /E /Y gonto-win.dist build\%OUTPUT_NAME%\
cd build
powershell Compress-Archive %OUTPUT_NAME% ..\dist\%OUTPUT_NAME%.zip
del /S /Q %OUTPUT_NAME%
cd ..
