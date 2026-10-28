"""
cumparaturi/urls.py

Maparea adreselor URL pentru cumpărături:
- Favorite / Wishlist (/favorite/ - R2.1)
- Coș de cumpărături (/cos/ - R2.2)
- Finalizare comandă / Checkout (/comanda/finalizare/ - R2.2)
- Confirmare comandă (/comanda/<id>/confirmare/ - R2.2)
- Istoric comenzi (/comenzi/ și /comenzi/<id>/ - R2.3)
- Gestiune comenzi pentru administratori (/administrare/comenzi/)
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
    # 2. Coșul de cumpărături (Cerința R2.2 — Prima parte)
    # -------------------------------------------------------------
    path('cos/', views.vizualizare_cos, name='vizualizare_cos'),
    path('cos/adauga/<int:produs_id>/', views.adaugare_in_cos, name='adaugare_in_cos'),
    path('cos/actualizeaza/<int:articol_id>/', views.actualizeaza_cos, name='actualizeaza_cos'),
    path('cos/elimina/<int:articol_id>/', views.elimina_din_cos, name='elimina_din_cos'),
    path('cos/cupon/aplica/', views.aplica_cod_reducere, name='aplica_cod_reducere'),
    path('cos/cupon/elimina/', views.elimina_cod_reducere, name='elimina_cod_reducere'),

    # -------------------------------------------------------------
    # 3. Finalizare și Confirmare Comandă (Cerința R2.2 — A doua parte)
    # -------------------------------------------------------------
    path('comanda/finalizare/', views.finalizare_comanda, name='finalizare_comanda'),
    path('comanda/<int:comanda_id>/confirmare/', views.confirmare_comanda, name='confirmare_comanda'),

    # -------------------------------------------------------------
    # 4. Istoric Comenzi (Cerința R2.3)
    # -------------------------------------------------------------
    path('comenzi/', views.istoric_comenzi, name='istoric_comenzi'),
    path('comenzi/<int:comanda_id>/', views.detaliu_comanda, name='detaliu_comanda'),

    # -------------------------------------------------------------
    # 5. Administrare Comenzi (Panou Admin)
    # -------------------------------------------------------------
    path('administrare/comenzi/', views.admin_comenzi_lista, name='admin_comenzi_lista'),
    path('administrare/comenzi/<int:comanda_id>/status/', views.admin_comanda_status, name='admin_comanda_status'),
]
