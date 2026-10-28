"""
cumparaturi/context_processors.py

Context processor pentru coșul de cumpărături și lista de favorite:
- Calculează numărul de articole din coș afișat în meniul site-ului (baza.html)
- Furnizează ID-urile produselor favorite pentru evidențierea inimilor pe carduri
"""

from .models import ArticolCos, Favorit


def cumparaturi_meniu(request):
    """Calculează contoarele pentru Coș și Favorite afișate în bara superioară."""
    if not request.user.is_authenticated:
        return {
            'numar_articole_cos': 0,
            'numar_favorite': 0,
            'utilizator_favorite_ids': set(),
        }

    # Pasul 1: Numărăm produsele din coș (suma cantităților sau numărul de poziții)
    numar_articole = ArticolCos.objects.filter(utilizator=request.user).count()

    # Pasul 2: Preluăm id-urile produselor din favorite pentru evidențiere pe carduri
    favorite_ids = set(
        Favorit.objects.filter(utilizator=request.user).values_list('produs_id', flat=True)
    )

    return {
        'numar_articole_cos': numar_articole,
        'numar_favorite': len(favorite_ids),
        'utilizator_favorite_ids': favorite_ids,
    }
