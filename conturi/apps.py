"""
conturi/apps.py

Configurarea aplicației Django 'conturi'.
Gestionează autentificarea, rolurile și profilurile de utilizatori.
"""

from django.apps import AppConfig


class ConturiConfig(AppConfig):
    """Configurația aplicației de conturi și roluri."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conturi'
    verbose_name = 'Conturi și Utilizatori'
