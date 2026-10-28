"""
cumparaturi/apps.py

Configurarea aplicației Django 'cumparaturi'.
Gestionează fluxul de e-commerce: coșul, favoritele și comenzile plasate.
"""

from django.apps import AppConfig


class CumparaturiConfig(AppConfig):
    """Configurația aplicației de cumpărături și comenzi."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cumparaturi'
    verbose_name = 'Cumpărături și Comenzi'
