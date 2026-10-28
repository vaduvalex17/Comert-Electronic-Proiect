"""
conturi/redirectionari.py

Funcție ajutătoare pentru redirecționări sigure.
După login (parametrul `?next=`) sau după un click pe „Adaugă în coș” / „Favorite”
(pagina de proveniență, header-ul `Referer`), aplicația îl trimite pe utilizator
„înapoi de unde a venit”. Adresa aceea vine însă din browser, deci poate fi
falsificată, iar fără verificare am putea trimite utilizatorul pe un site străin
(atac de tip „open redirect”). Este folosită de conturi/views.py și cumparaturi/views.py.
"""

from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def redirectioneaza_sigur(request, adresa, adresa_implicita):
    """Redirecționează la `adresa` doar dacă aparține site-ului nostru; altfel la `adresa_implicita`.

    `adresa_implicita` poate fi un URL sau numele unei rute (ex: 'catalog:acasa').
    """
    # Verificăm că adresa e relativă (ex: /cos/) sau are același domeniu ca site-ul curent
    if adresa and url_has_allowed_host_and_scheme(
        adresa,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(adresa)
    return redirect(adresa_implicita)
