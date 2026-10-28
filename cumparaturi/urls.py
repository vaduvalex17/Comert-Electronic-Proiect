"""
cumparaturi/urls.py

Maparea adreselor URL pentru coș, comenzi și lista de favorite:
- Favorite (R2.1): vizualizare listă, toggle adăugare/eliminare, ștergere, mutare în coș
"""

from django.urls import path
from . import views

app_name = 'cumparaturi'

urlpatterns = [
    # -------------------------------------------------------------
    # 1. Lista de Favorite / Wishlist (Cerința R2.1)
    # -------------------------------------------------------------
    path('favorite/', views.lista_favorite, name='lista_favorite'),
    path('favorite/toggle/<int:produs_id>/', views.adauga_elimina_favorit, name='adauga_elimina_favorit'),
    path('favorite/<int:favorit_id>/elimina/', views.elimina_favorit, name='elimina_favorit'),
    path('favorite/<int:favorit_id>/muta-in-cos/', views.muta_in_cos, name='muta_in_cos'),
]
