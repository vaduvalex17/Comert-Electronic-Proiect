@echo off
REM pornire.bat
REM Script automat pentru configurarea și pornirea magazinului online pe Windows.

echo ==========================================================
echo    PORNIRE MAGAZIN ONLINE - COMERT ELECTRONIC (TEMA II)   
echo ==========================================================

REM Pasul 1: Verificare / creare mediu virtual Python
if not exist "venv" (
    echo [1/4] Creez mediul virtual Python (venv)...
    python -m venv venv
) else (
    echo [1/4] Mediul virtual 'venv' exista deja.
)

REM Activare mediu virtual
call venv\Scripts\activate.bat

REM Pasul 2: Instalare sau actualizare pachete necesare
echo [2/4] Verific dependentele din requirements.txt...
pip install -q -r requirements.txt

REM Pasul 3: Aplicare migrari in baza de date SQLite
echo [3/4] Sincronizez baza de date (migrari)...
python manage.py migrate --noinput

REM Populare date demo (daca comanda 'populeaza_date' este definita)
python manage.py help populeaza_date >nul 2>&1
if %errorlevel% equ 0 (
    echo        Verific / incarc datele demo (produse, conturi de test)...
    python manage.py populeaza_date
)

REM Pasul 4: Pornire server de dezvoltare
echo [4/4] Pornesc serverul web...
echo ----------------------------------------------------------
echo  Magazinul este disponibil la adresa: http://127.0.0.1:8000
echo  Pentru a opri serverul, apasa CTRL + C in aceasta fereastra.
echo ----------------------------------------------------------
python manage.py runserver 127.0.0.1:8000
pause
