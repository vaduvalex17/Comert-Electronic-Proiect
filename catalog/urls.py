"""
catalog/urls.py

Maparea adreselor URL pentru catalogul de produse (partea publică a magazinului).
"""

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Pagina principală a magazinului (Acasă)
    path('', views.acasa, name='acasa'),

    # Lista tuturor produselor și căutare (?q=...)
    path('produse/', views.lista_produse, name='lista_produse'),

    # Produsele dintr-o anumită categorie
    path('categorie/<slug:slug>/', views.produse_categorie, name='produse_categorie'),

    # Pagina de detaliu a unui produs individual (cerința R1.3)
    path('produs/<slug:slug>/', views.detaliu_produs, name='detaliu_produs'),
]
