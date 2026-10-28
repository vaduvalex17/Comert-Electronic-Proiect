"""
catalog/models.py

Modelele bazei de date pentru catalogul magazinului:
- Categorie: grupează produsele
- Furnizor: compania parteneră
- ModalitateLivrare: metodele de expediere disponibile
- Produs: entitatea principală cu specificații, stoc și preț

Modelele detaliate sunt definite în Faza 1.
"""

from django.db import models
