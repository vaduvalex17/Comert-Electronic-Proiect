@echo off
REM pornire.bat
REM Script automat pentru configurarea si pornirea magazinului online pe Windows.
REM Se porneste cu dublu click. Pasii: gaseste Python - il instaleaza singur daca lipseste,
REM creeaza mediul virtual, instaleaza pachetele, pregateste baza de date, incarca datele
REM demo, porneste serverul si deschide browserul cand magazinul este gata.
REM
REM ATENTIE pentru cine modifica fisierul: in interiorul blocurilor if ( ... ) NU folositi
REM paranteze in textele afisate cu echo. Windows ar citi ")" ca sfarsitul blocului
REM si scriptul s-ar opri cu eroare. De aceea logica foloseste "goto" in loc de blocuri.

REM Rulam scriptul din folderul in care se afla, chiar daca e pornit din alta parte
cd /d "%~dp0"
title Magazin Online - NU INCHIDE ACEASTA FEREASTRA

echo ==========================================================
echo    PORNIRE MAGAZIN ONLINE - COMERT ELECTRONIC - TEMA II
echo ==========================================================

REM Pasul 0: Gasim Python 3.10+ - daca lipseste, il instalam automat
call :gaseste_python
if not defined PY goto :eroare
echo        Python gasit: %PY%

REM Pasul 1: Verificare / creare mediu virtual Python - folderul venv
if exist "venv\Scripts\activate.bat" goto :venv_exista
echo [1/4] Creez mediul virtual Python - folderul venv...
"%PY%" -m venv venv
if errorlevel 1 goto :eroare
goto :activare
:venv_exista
echo [1/4] Mediul virtual venv exista deja.

:activare
call venv\Scripts\activate.bat

REM Pasul 2: Instalare pachete necesare - Django si Pillow
echo [2/4] Verific dependentele din requirements.txt...
python -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :eroare

REM Pasul 3: Aplicare migrari in baza de date SQLite
echo [3/4] Sincronizez baza de date - migrari...
python manage.py migrate --noinput
if errorlevel 1 goto :eroare

REM Incarcam datele demo - produse, conturi de test; comanda nu creeaza dubluri
echo        Verific / incarc datele demo - produse, conturi de test...
python manage.py populeaza_date
if errorlevel 1 goto :eroare

REM Pasul 4: Alegem un port liber - 8000, iar daca e ocupat, urmatorul
set "PORT=8000"
:alege_port
call :port_ocupat %PORT%
if errorlevel 1 goto :port_ales
echo        Portul %PORT% este ocupat de alt program, incerc urmatorul.
set /a PORT+=1
goto :alege_port
:port_ales

echo [4/4] Pornesc serverul web...
echo ----------------------------------------------------------
echo  Magazinul se deschide singur in browser in cateva secunde.
echo  Daca nu se deschide, scrie in browser: http://127.0.0.1:%PORT%
echo  Cont admin: admin / admin123     Cont client: client / client123
echo  NU inchide aceasta fereastra cat timp folosesti magazinul.
echo  Pentru a opri serverul, inchide fereastra sau apasa CTRL + C.
echo ----------------------------------------------------------

REM In fundal: asteptam pana raspunde site-ul, apoi deschidem browserul
start "" /b powershell -NoProfile -ExecutionPolicy Bypass -Command "for ($i = 0; $i -lt 120; $i++) { try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1', %PORT%); $c.Close(); Start-Process 'http://127.0.0.1:%PORT%/'; break } catch { Start-Sleep -Seconds 1 } }"

python manage.py runserver 127.0.0.1:%PORT%
pause
exit /b 0

:eroare
REM Afisam un mesaj si tinem fereastra deschisa, ca eroarea sa poata fi citita
echo.
echo [EROARE] Pornirea a esuat. Citeste mesajul de mai sus si vezi
echo sectiunea "Probleme frecvente" din docs\00-START-AICI.md
pause
exit /b 1

REM ==========================================================
REM Subrutine
REM ==========================================================

:port_ocupat
REM Intoarce 0 daca pe portul primit raspunde deja ceva pe acest calculator, altfel 1.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1', %1); $c.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
exit /b %errorlevel%

:gaseste_python
REM Pune in variabila PY calea catre un Python 3.10+ . Daca nu exista, il instaleaza
REM automat cu winget - doar pentru utilizatorul curent - sau deschide pagina de descarcare.
set "PY="
set "VERIFICA=import sys; print(sys.executable) if sys.version_info >= (3, 10) else None"
call :cauta_python
if defined PY exit /b 0
echo.
echo  Python nu este instalat pe acest calculator.
echo  Il instalez acum automat. Dureaza 1-3 minute si are nevoie de internet.
echo  Daca Windows intreaba daca permiti modificari, apasa "Da".
echo.
where winget >nul 2>nul
if errorlevel 1 goto :fara_winget
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
call :cauta_python
if defined PY exit /b 0
echo.
echo  Python s-a instalat. Inchide aceasta fereastra si da din nou
echo  dublu click pe pornire.bat.
exit /b 0

:fara_winget
echo  Nu pot instala Python automat pe acest calculator.
echo  Se deschide pagina de descarcare: apasa butonul galben "Download Python",
echo  porneste fisierul descarcat, BIFEAZA "Add python.exe to PATH" jos in fereastra,
echo  apoi apasa "Install Now". La final, da din nou dublu click pe pornire.bat.
start "" https://www.python.org/downloads/windows/
exit /b 0

:cauta_python
REM Cauta Python in locurile obisnuite; seteaza PY daca il gaseste.
for /f "delims=" %%i in ('py -3 -c "%VERIFICA%" 2^>nul') do set "PY=%%i"
if defined PY exit /b 0
for /f "delims=" %%i in ('python -c "%VERIFICA%" 2^>nul') do set "PY=%%i"
if defined PY exit /b 0
for %%v in (314 313 312) do if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe"
exit /b 0
