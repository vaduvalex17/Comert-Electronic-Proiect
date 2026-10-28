"""
cumparaturi/urls.py

Maparea adreselor URL pentru cumpărături:
- Favorite / Wishlist (R2.1)
- Coș de cumpărături (R2.2)
"""

from django.urls import path
from . import views

app_name = 'cumparaturi'

urlpatterns = [
    # -------------------------------------------------------------
    # 1. Favorite / Wishlist (Cerința R2.1)
    # -------------------------------------------------------------
    path('favorite/', views.lista_favorite, name='lista_favorite'),
    path('favorite/toggle/<int:produs_id>/', views.adauga_elimina_favorit, name='adauga_elimina_favorit'),
    path('favorite/<int:favorit_id>/elimina/', views.elimina_favorit, name='elimina_favorit'),
    path('favorite/<int:favorit_id>/muta-in-cos/', views.muta_in_cos, name='muta_in_cos'),

    # -------------------------------------------------------------
    # 2. Coșul de cumpărături (Cerința R2.2)
    # -------------------------------------------------------------
    path('cos/', views.vizualizare_cos, name='vizualizare_cos'),
    path('cos/adauga/<int:produs_id>/', views.adaugare_in_cos, name='adaugare_in_cos'),
    path('cos/actualizeaza/<int:articol_id>/', views.actualizeaza_cos, name='actualizeaza_cos'),
    path('cos/elimina/<int:articol_id>/', views.elimina_din_cos, name='elimina_din_cos'),
]
