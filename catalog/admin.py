"""
catalog/admin.py

Înregistrarea modelelor de catalog în panoul de administrare Django (/admin/).
Configurat cu filtre, căutare și afișare tabelară pentru o navigare facilă.
"""

from django.contrib import admin
from .models import Categorie, Furnizor, ModalitateLivrare, Produs


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """Configurarea administrării categoriilor."""

    list_display = ('nume', 'slug')
    search_fields = ('nume', 'descriere')
    prepopulated_fields = {'slug': ('nume',)}


@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    """Configurarea administrării furnizorilor."""

    list_display = ('nume', 'email', 'telefon')
    search_fields = ('nume', 'email', 'telefon')


@admin.register(ModalitateLivrare)
class ModalitateLivrareAdmin(admin.ModelAdmin):
    """Configurarea modalităților de livrare."""

    list_display = ('nume', 'cost', 'zile_estimate')
    list_filter = ('zile_estimate',)
    search_fields = ('nume',)


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    """Configurarea administrării produselor în panoul Django."""

    list_display = ('nume', 'categorie', 'pret', 'stoc', 'furnizor', 'activ', 'creat_la')
    list_filter = ('activ', 'categorie', 'furnizor', 'modalitati_livrare')
    search_fields = ('nume', 'descriere', 'specificatii')
    prepopulated_fields = {'slug': ('nume',)}
    list_editable = ('pret', 'stoc', 'activ')
    filter_horizontal = ('modalitati_livrare',)
