"""
cumparaturi/models.py

Modelele bazei de date pentru fluxurile de cumpărare:
- Favorit: produse salvate în wishlist de către clienți
- ArticolCos: produsele adăugate în coșul curent
- Comanda: antetul comenzii plasate
- ArticolComanda: liniile de comandă (copie fixă / snapshot de preț)

Modelele detaliate sunt definite în Faza 1.
"""

from django.db import models
