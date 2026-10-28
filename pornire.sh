#!/usr/bin/env bash
# pornire.sh
# Script automat pentru configurarea și pornirea magazinului online pe Linux / macOS.
# Acest script se asigură că mediul virtual există, dependențele sunt instalate,
# migrările sunt aplicate și serverul este pornit.

set -e

echo "=========================================================="
echo "   PORNIRE MAGAZIN ONLINE — COMERȚ ELECTRONIC (TEMA II)   "
echo "=========================================================="

# Pasul 1: Verificare / creare mediu virtual Python
if [ ! -d "venv" ]; then
    echo "[1/4] Creez mediul virtual Python (venv)..."
    python3 -m venv venv
else
    echo "[1/4] Mediul virtual 'venv' există deja."
fi

# Activare mediu virtual
source venv/bin/activate

# Pasul 2: Instalare sau actualizare pachete necesare
echo "[2/4] Verific dependențele din requirements.txt..."
pip install -q -r requirements.txt

# Pasul 3: Aplicare migrări în baza de date SQLite
echo "[3/4] Sincronizez baza de date (migrări)..."
python manage.py migrate --noinput

# Populare date demo (dacă comanda de management 'populeaza_date' este disponibilă)
if python manage.py help populeaza_date > /dev/null 2>&1; then
    echo "       Verific / încarc datele demo (produse, conturi de test)..."
    python manage.py populeaza_date
fi

# Pasul 4: Pornire server de dezvoltare
echo "[4/4] Pornesc serverul web..."
echo "----------------------------------------------------------"
echo " Magazinul este disponibil la adresa: http://127.0.0.1:8000"
echo " Pentru a opri serverul, apasă CTRL + C în această fereastră."
echo "----------------------------------------------------------"
python manage.py runserver 127.0.0.1:8000
