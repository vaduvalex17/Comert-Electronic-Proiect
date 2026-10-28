"""
conturi/decoratori.py

Decoratori personalizați pentru protejarea paginilor magazinului în funcție de rol.
Decoratorul `@doar_admin` garantează că doar utilizatorii cu drepturi de administrator
(is_staff == True) pot accesa secțiunile sensibile (panoul de CRUD produse).
"""

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def doar_admin(view_func):
    """Restricționează accesul la o pagină exclusiv pentru administratori (staff).

    - Dacă utilizatorul nu este autentificat: îl trimite la pagina de login.
    - Dacă utilizatorul este client obișnuit (non-staff): afișează o eroare și îl trimite pe Acasă.
    - Dacă utilizatorul este admin (is_staff=True): permite executarea funcției din view.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Pasul 1: Verificăm dacă utilizatorul este logat
        if not request.user.is_authenticated:
            messages.warning(request, "Trebuie să fii autentificat ca administrator pentru a accesa această pagină.")
            return redirect('conturi:login')

        # Pasul 2: Verificăm dacă are rolul de staff/admin
        if not request.user.is_staff:
            messages.error(request, "Acces refuzat! Această pagină este destinată exclusiv administratorilor magazinului.")
            return redirect('catalog:acasa')

        # Pasul 3: Utilizatorul este admin, permitem accesul
        return view_func(request, *args, **kwargs)

    return wrapper
