"""
catalog/context_processors.py

Context processor care face categoriile active disponibile automat în toate șabloanele HTML
(în special în bara de navigare din baza.html), fără a fi nevoie să le transmitem manual din fiecare view.
"""

from .models import Categorie


def categorii_globale(request):
    """Returnează toate categoriile ordonate alfabetic pentru meniul de sus."""
    return {
        'categorii_meniu': Categorie.objects.all().order_by('nume')
    }
