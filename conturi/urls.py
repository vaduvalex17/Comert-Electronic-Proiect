"""
conturi/urls.py

Rutele pentru autentificare, deconectare și crearea conturilor de utilizator.
"""

from django.urls import path
from . import views

app_name = 'conturi'

urlpatterns = [
    # Autentificare în cont
    path('login/', views.login_utilizator, name='login'),

    # Deconectare din sesiune (POST)
    path('logout/', views.logout_utilizator, name='logout'),

    # Înregistrare client nou
    path('inregistrare/', views.inregistrare_utilizator, name='inregistrare'),
]
