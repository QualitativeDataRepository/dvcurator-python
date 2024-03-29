@echo off
C:
cd \
mkdir Apps-SU

set PROG=dvcurator
set EXE=C:\Apps-SU\%PROG%_win.exe
set LNK=H:\Desktop\%PROG%.url

for /f "tokens=1,* delims=:" %%A in ('curl -ks https://api.github.com/repos/QualitativeDataRepository/dvcurator-python/releases/latest ^| find "browser_download_url" ^| findstr exe') do (
    curl -kL %%B -o %EXE%
)

echo [InternetShortcut] >> %LNK%
echo URL=%EXE% >> %LNK%
echo IconFile=%EXE% >> %LNK%
echo IconIndex=0 >> %LNK%

echo Install complete!
pause
