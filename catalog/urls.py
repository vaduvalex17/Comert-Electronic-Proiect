"""
catalog/urls.py

Maparea adreselor URL pentru catalogul de produse:
- Partea publică: Acasă, catalog, filtrare categorie, detaliu produs
- Panoul de administrare produse (R1.2): listă, adăugare, editare, ștergere (soft-delete)
"""

from django.urls import path
from . import views, views_admin

app_name = 'catalog'

urlpatterns = [
    # -------------------------------------------------------------
    # 1. Rute publice (Catalog & Căutare - R1.3, R1.4)
    # -------------------------------------------------------------
    path('', views.acasa, name='acasa'),
    path('produse/', views.lista_produse, name='lista_produse'),
    path('categorie/<slug:slug>/', views.produse_categorie, name='produse_categorie'),
    path('produs/<slug:slug>/', views.detaliu_produs, name='detaliu_produs'),

    # -------------------------------------------------------------
    # 2. Rute panou de administrare produse (CRUD Admin - R1.2)
    # -------------------------------------------------------------
    path('administrare/produse/', views_admin.admin_produse_lista, name='admin_produse_lista'),
    path('administrare/produse/adauga/', views_admin.admin_produs_adauga, name='admin_produs_adauga'),
    path('administrare/produse/<int:pk>/editeaza/', views_admin.admin_produs_editeaza, name='admin_produs_editeaza'),
    path('administrare/produse/<int:pk>/sterge/', views_admin.admin_produs_sterge, name='admin_produs_sterge'),
]
