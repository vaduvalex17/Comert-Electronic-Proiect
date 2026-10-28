@echo off
REM pornire.bat
REM Script automat pentru configurarea si pornirea magazinului online pe Windows.
REM Se porneste cu dublu click. Pasii: verifica Python, creeaza mediul virtual,
REM instaleaza pachetele, pregateste baza de date, incarca datele demo, porneste serverul.
REM
REM ATENTIE pentru cine modifica fisierul: in interiorul blocurilor if ( ... ) NU folositi
REM paranteze in textele afisate cu echo. Windows ar citi ")" ca sfarsitul blocului
REM si scriptul s-ar opri cu eroare. Textele de mai jos folosesc "-" in loc de paranteze.

REM Rulam scriptul din folderul in care se afla, chiar daca e pornit din alta parte
cd /d "%~dp0"

echo ==========================================================
echo    PORNIRE MAGAZIN ONLINE - COMERT ELECTRONIC - TEMA II
echo ==========================================================

REM Pasul 0: Verificam ca Python este instalat
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [EROARE] Python nu a fost gasit pe acest calculator.
    echo Instaleaza Python 3.12 sau mai nou de pe https://www.python.org/downloads/
    echo La instalare bifeaza obligatoriu casuta "Add python.exe to PATH".
    goto :eroare
)

REM Pasul 1: Verificare / creare mediu virtual Python - folderul venv
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creez mediul virtual Python - folderul venv...
    python -m venv venv
    if errorlevel 1 goto :eroare
) else (
    echo [1/4] Mediul virtual venv exista deja.
)

REM Activare mediu virtual
call venv\Scripts\activate.bat

REM Pasul 2: Instalare pachete necesare - Django si Pillow
echo [2/4] Verific dependentele din requirements.txt...
python -m pip install -q -r requirements.txt
if errorlevel 1 goto :eroare

REM Pasul 3: Aplicare migrari in baza de date SQLite
echo [3/4] Sincronizez baza de date - migrari...
python manage.py migrate --noinput
if errorlevel 1 goto :eroare

REM Incarcam datele demo - produse, conturi de test; comanda nu creeaza dubluri
echo        Verific / incarc datele demo - produse, conturi de test...
python manage.py populeaza_date
if errorlevel 1 goto :eroare

REM Pasul 4: Pornire server de dezvoltare
echo [4/4] Pornesc serverul web...
echo ----------------------------------------------------------
echo  Magazinul este disponibil la adresa: http://127.0.0.1:8000
echo  Cont admin: admin / admin123     Cont client: client / client123
echo  Pentru a opri serverul, apasa CTRL + C in aceasta fereastra.
echo ----------------------------------------------------------
python manage.py runserver 127.0.0.1:8000
pause
exit /b 0

:eroare
REM Afisam un mesaj si tinem fereastra deschisa, ca eroarea sa poata fi citita
echo.
echo [EROARE] Pornirea a esuat. Citeste mesajul de mai sus si vezi
echo sectiunea "Probleme frecvente" din docs\00-START-AICI.md
pause
exit /b 1
