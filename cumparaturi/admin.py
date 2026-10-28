"""
cumparaturi/admin.py

Înregistrarea comenzilor, favoritelor și coșurilor în panoul Django Admin.
Permite administratorului să vizualizeze comenzile și articolele conținute.
"""

from django.contrib import admin
from .models import ArticolComanda, ArticolCos, CodReducere, Comanda, Favorit


@admin.register(CodReducere)
class CodReducereAdmin(admin.ModelAdmin):
    """Administrarea codurilor promoționale de reducere."""

    list_display = ('cod', 'procent_reducere', 'valoare_minima_comanda', 'activ', 'data_expirare')
    list_filter = ('activ', 'data_expirare')
    search_fields = ('cod',)


class ArticolComandaInline(admin.TabularInline):
    """Afișează produsele comandate direct în interiorul paginii de comandă."""

    model = ArticolComanda
    extra = 0
    readonly_fields = ('nume_produs', 'pret_unitar', 'cantitate', 'subtotal')


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    """Administrarea comenzilor clienților."""

    list_display = ('id', 'utilizator', 'nume_destinatar', 'oras', 'total', 'status', 'creata_la')
    list_filter = ('status', 'modalitate_livrare', 'creata_la')
    search_fields = ('id', 'nume_destinatar', 'telefon', 'adresa', 'oras', 'utilizator__username')
    readonly_fields = ('creata_la', 'subtotal', 'cost_livrare', 'total', 'card_ultimele4')
    inlines = [ArticolComandaInline]


@admin.register(Favorit)
class FavoritAdmin(admin.ModelAdmin):
    """Vizualizarea produselor favorite salvate de utilizatori."""

    list_display = ('utilizator', 'produs', 'adaugat_la')
    list_filter = ('adaugat_la',)
    search_fields = ('utilizator__username', 'produs__nume')


@admin.register(ArticolCos)
class ArticolCosAdmin(admin.ModelAdmin):
    """Vizualizarea coșurilor active ale utilizatorilor."""

    list_display = ('utilizator', 'produs', 'cantitate', 'adaugat_la', 'subtotal')
    search_fields = ('utilizator__username', 'produs__nume')
