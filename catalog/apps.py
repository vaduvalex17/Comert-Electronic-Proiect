"""
catalog/apps.py

Configurarea aplicației Django 'catalog'.
Gestionează catalogul comercial: categorii, produse, furnizori și livrări.
"""

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Configurația aplicației de catalog și administrare produse."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
    verbose_name = 'Catalog Produse'
