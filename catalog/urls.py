"""
catalog/urls.py

Maparea adreselor URL pentru catalogul de produse (partea publică).
"""

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Pagina principală a magazinului
    path('', views.acasa, name='acasa'),
]
