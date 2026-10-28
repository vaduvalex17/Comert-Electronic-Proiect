"""
cumparaturi/context_processors.py

Context processor pentru coșul de cumpărături și lista de favorite:
- Calculează numărul total de unități din coș afișat în meniul site-ului (baza.html)
- Furnizează ID-urile produselor favorite pentru evidențierea inimilor pe carduri
"""

from django.db.models import Sum
from .models import ArticolCos, Favorit


def cumparaturi_meniu(request):
    """Calculează contoarele pentru Coș și Favorite afișate în bara superioară."""
    if not request.user.is_authenticated:
        return {
            'numar_articole_cos': 0,
            'numar_favorite': 0,
            'utilizator_favorite_ids': set(),
        }

    # Pasul 1: Numărăm totalul unităților din coș (suma cantităților)
    total_bucati_cos = ArticolCos.objects.filter(
        utilizator=request.user
    ).aggregate(total=Sum('cantitate'))['total'] or 0

    # Pasul 2: Preluăm id-urile produselor din favorite pentru evidențiere pe carduri
    favorite_ids = set(
        Favorit.objects.filter(utilizator=request.user).values_list('produs_id', flat=True)
    )

    return {
        'numar_articole_cos': total_bucati_cos,
        'numar_favorite': len(favorite_ids),
        'utilizator_favorite_ids': favorite_ids,
    }
