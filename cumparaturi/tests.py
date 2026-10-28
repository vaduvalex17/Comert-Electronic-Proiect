"""
cumparaturi/tests.py

Teste automate pentru modelele aplicației de cumpărături:
- Calculul subtotalului pe articol de coș (cantitate * preț)
- Calculul subtotalului pe linie de comandă istorică
- Unicitatea produsului în coș per utilizator
- Unicitatea produsului în favorite per utilizator
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from catalog.models import Categorie, Furnizor, ModalitateLivrare, Produs
from cumparaturi.models import ArticolComanda, ArticolCos, Comanda, Favorit

User = get_user_model()


class ModeleCumparaturiTest(TestCase):
    """Teste pentru calculul corect al sumelor și integritatea datelor de cumpărături."""

    def setUp(self):
        """Configurează utilizatorul și produsele de test."""
        self.user = User.objects.create_user(
            username='client_test',
            password='parola123'
        )
        self.cat = Categorie.objects.create(nume='Audio')
        self.furnizor = Furnizor.objects.create(
            nume='Furnizor Audio SRL',
            email='audio@furnizor.ro',
            telefon='0799111222'
        )
        self.livrare = ModalitateLivrare.objects.create(
            nume='Curier Rapid',
            cost=Decimal('15.00')
        )
        self.produs = Produs.objects.create(
            nume='Căști Bluetooth',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('150.00'),
            stoc=10
        )

    def test_calcul_subtotal_articol_cos(self):
        """Verifică calculul corect al proprietății subtotal din coș."""
        articol = ArticolCos.objects.create(
            utilizator=self.user,
            produs=self.produs,
            cantitate=3
        )
        # 3 bucăți * 150.00 lei = 450.00 lei
        self.assertEqual(articol.subtotal, Decimal('450.00'))

    def test_unicitate_articol_cos_per_utilizator(self):
        """Verifică faptul că același produs nu poate apărea de două ori ca linie separată în coș."""
        ArticolCos.objects.create(
            utilizator=self.user,
            produs=self.produs,
            cantitate=1
        )
        with self.assertRaises(IntegrityError):
            ArticolCos.objects.create(
                utilizator=self.user,
                produs=self.produs,
                cantitate=2
            )

    def test_unicitate_favorit_per_utilizator(self):
        """Verifică că un produs poate fi adăugat o singură dată în favorite de un utilizator."""
        Favorit.objects.create(
            utilizator=self.user,
            produs=self.produs
        )
        with self.assertRaises(IntegrityError):
            Favorit.objects.create(
                utilizator=self.user,
                produs=self.produs
            )

    def test_snapshot_articol_comanda(self):
        """Verifică că ArticolComanda păstrează snapshot-ul de preț independent de schimbările viitoare."""
        comanda = Comanda.objects.create(
            utilizator=self.user,
            nume_destinatar='Ion Popescu',
            telefon='0722333444',
            adresa='Str. Florilor 1',
            oras='București',
            judet='Sector 1',
            cod_postal='010101',
            modalitate_livrare=self.livrare,
            cost_livrare=self.livrare.cost,
            subtotal=Decimal('300.00'),
            total=Decimal('315.00')
        )

        linie = ArticolComanda.objects.create(
            comanda=comanda,
            produs=self.produs,
            nume_produs=self.produs.nume,
            pret_unitar=self.produs.pret,  # 150.00
            cantitate=2
        )
        self.assertEqual(linie.subtotal, Decimal('300.00'))

        # Modificăm prețul produsului în catalog (de exemplu o scumpire la 200.00 lei)
        self.produs.pret = Decimal('200.00')
        self.produs.save()

        # Reîncărcăm linia de comandă: prețul istoric din comandă trebuie să rămână 150.00 lei
        linie.refresh_from_db()
        self.assertEqual(linie.pret_unitar, Decimal('150.00'))
        self.assertEqual(linie.subtotal, Decimal('300.00'))
