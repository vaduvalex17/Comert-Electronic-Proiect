"""
cumparaturi/models.py

Modelele bazei de date pentru procesul de achiziție:
- Favorit: lista de dorințe (Wishlist) conform cerinței R2.1
- ArticolCos: produsele din coșul clientului conform cerinței R2.2
- Comanda: datele de livrare, metoda de livrare, totalul și snapshot-ul de card conform cerințelor R2.2 și R2.3
- ArticolComanda: produsele comandate, cu salvarea prețului istoric din momentul achiziției
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Favorit(models.Model):
    """Articol salvat de utilizator în lista de produse favorite (Wishlist).

    Cerința R2.1: permite clienților să marcheze produsele dorite pentru mai târziu.
    """

    utilizator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name="Utilizator"
    )
    produs = models.ForeignKey(
        'catalog.Produs',
        on_delete=models.CASCADE,
        related_name='favoriti',
        verbose_name="Produs salvat"
    )
    adaugat_la = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data salvării"
    )

    class Meta:
        verbose_name = "Favorit"
        verbose_name_plural = "Favorite"
        unique_together = ('utilizator', 'produs')
        ordering = ['-adaugat_la']

    def __str__(self):
        return f"{self.utilizator.username} -> {self.produs.nume}"


class ArticolCos(models.Model):
    """Produs adăugat de utilizator în coșul curent de cumpărături.

    Cerința R2.2: coșul este salvat în baza de date pentru persistență între autentificări.
    """

    utilizator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articole_cos',
        verbose_name="Utilizator"
    )
    produs = models.ForeignKey(
        'catalog.Produs',
        on_delete=models.CASCADE,
        related_name='articole_in_cos',
        verbose_name="Produs"
    )
    cantitate = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Cantitate dorită"
    )
    adaugat_la = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data adăugării în coș"
    )

    class Meta:
        verbose_name = "Articol coș"
        verbose_name_plural = "Articole coș"
        unique_together = ('utilizator', 'produs')

    def __str__(self):
        return f"{self.cantitate}x {self.produs.nume} ({self.utilizator.username})"

    @property
    def subtotal(self):
        """Calculează valoarea totală pentru acest articol (preț produs * cantitate)."""
        return self.produs.pret * self.cantitate


class Comanda(models.Model):
    """Comandă finalizată de către un client.

    Cerințele R2.2 și R2.3: înregistrează toate detaliile de livrare,
    metoda de transport, costul și ultimele 4 cifre ale cardului folosit.
    """

    STATUS_ALEGERI = [
        ('plasata', 'Plasată'),
        ('in_procesare', 'În procesare'),
        ('livrata', 'Livrată'),
        ('anulata', 'Anulată'),
    ]

    utilizator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='comenzi',
        verbose_name="Client"
    )
    creata_la = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data plasării"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_ALEGERI,
        default='plasata',
        verbose_name="Starea comenzii"
    )

    # Date de livrare (R2.2)
    nume_destinatar = models.CharField(
        max_length=150,
        verbose_name="Nume destinatar"
    )
    telefon = models.CharField(
        max_length=20,
        verbose_name="Număr de telefon"
    )
    adresa = models.CharField(
        max_length=255,
        verbose_name="Adresă livrare"
    )
    oras = models.CharField(
        max_length=100,
        verbose_name="Oraș"
    )
    judet = models.CharField(
        max_length=100,
        verbose_name="Județ / Sector"
    )
    cod_postal = models.CharField(
        max_length=20,
        verbose_name="Cod poștal"
    )

    # Modalitatea de livrare și calculul financiar
    modalitate_livrare = models.ForeignKey(
        'catalog.ModalitateLivrare',
        on_delete=models.PROTECT,
        related_name='comenzi',
        verbose_name="Modalitate de livrare"
    )
    cost_livrare = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Cost livrare (lei)"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Subtotal produse (lei)"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total comandă (lei)"
    )

    # Plată sigură: doar ultimele 4 cifre sunt păstrate pentru identificare (CVV-ul NU se salvează!)
    card_ultimele4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="Ultimele 4 cifre ale cardului"
    )

    class Meta:
        verbose_name = "Comandă"
        verbose_name_plural = "Comenzi"
        ordering = ['-creata_la']

    def __str__(self):
        return f"Comanda #{self.id} — {self.creata_la.strftime('%d.%m.%Y %H:%M')}"


class ArticolComanda(models.Model):
    """Linie individuală de produs dintr-o comandă finalizată.

    IMPORTANT: Salvează numele și prețul din momentul achiziției (snapshot),
    pentru ca eventuale modificări viitoare de preț să nu altereze valoarea comenzii istorice.
    """

    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='articole',
        verbose_name="Comandă"
    )
    produs = models.ForeignKey(
        'catalog.Produs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linii_comanda',
        verbose_name="Produs de referință"
    )
    nume_produs = models.CharField(
        max_length=200,
        verbose_name="Denumire produs la momentul cumpărării"
    )
    pret_unitar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preț unitar la cumpărare (lei)"
    )
    cantitate = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantitate comandată"
    )

    class Meta:
        verbose_name = "Articol comandă"
        verbose_name_plural = "Articole comandă"

    def __str__(self):
        return f"{self.cantitate}x {self.nume_produs} (Comanda #{self.comanda_id})"

    @property
    def subtotal(self):
        """Valoarea totală a acestei linii din comandă."""
        return self.pret_unitar * self.cantitate
