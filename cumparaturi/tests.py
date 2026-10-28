"""
cumparaturi/tests.py

Teste automate pentru modulul de cumpărături:
- Modele: calcul subtotal coș, calcul subtotal linie comandă, unicități și snapshot-uri
- Favorite (Cerința R2.1): acces restricționat pentru anonimi, toggle adăugare/eliminare,
  ștergere directă din listă, mutare în coș pentru produse în stoc și verificare stoc epuizat.
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
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
            pret_unitar=self.produs.pret,
            cantitate=2
        )
        self.assertEqual(linie.subtotal, Decimal('300.00'))

        self.produs.pret = Decimal('200.00')
        self.produs.save()

        linie.refresh_from_db()
        self.assertEqual(linie.pret_unitar, Decimal('150.00'))
        self.assertEqual(linie.subtotal, Decimal('300.00'))


class FavoriteFlowTest(TestCase):
    """Teste complete pentru lista de favorite / wishlist (Cerința R2.1)."""

    def setUp(self):
        """Pregătește utilizatori și produse pentru testele de favorite."""
        self.client_user = User.objects.create_user(
            username='cumpărător_test',
            password='parola_client'
        )
        self.cat = Categorie.objects.create(nume='Audio', slug='audio')
        self.furnizor = Furnizor.objects.create(
            nume='Furnizor Sound',
            email='sound@test.ro',
            telefon='0733000111'
        )
        self.produs_stoc = Produs.objects.create(
            nume='Boxă JBL Go',
            slug='boxa-jbl-go',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('199.00'),
            stoc=5,
            activ=True
        )
        self.produs_epuizat = Produs.objects.create(
            nume='Boxă JBL Go 2 (Epuizată)',
            slug='boxa-jbl-go-2',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('220.00'),
            stoc=0,
            activ=True
        )

    def test_acces_favorite_necesita_autentificare(self):
        """Un vizitator neautentificat este redirecționat la login dacă accesează /favorite/."""
        raspuns = self.client.get(reverse('cumparaturi:lista_favorite'))
        self.assertRedirects(raspuns, f"{reverse('conturi:login')}?next={reverse('cumparaturi:lista_favorite')}")

    def test_adaugare_si_eliminare_prin_toggle(self):
        """Verifică adăugarea și eliminarea alternativă din favorite prin apel POST."""
        self.client.login(username='cumpărător_test', password='parola_client')

        # 1. Adăugare în favorite
        raspuns1 = self.client.post(reverse('cumparaturi:adauga_elimina_favorit', kwargs={'produs_id': self.produs_stoc.id}))
        self.assertTrue(Favorit.objects.filter(utilizator=self.client_user, produs=self.produs_stoc).exists())

        # 2. Re-apelare toggle pe același produs -> îl elimină
        raspuns2 = self.client.post(reverse('cumparaturi:adauga_elimina_favorit', kwargs={'produs_id': self.produs_stoc.id}))
        self.assertFalse(Favorit.objects.filter(utilizator=self.client_user, produs=self.produs_stoc).exists())

    def test_vizualizare_lista_favorite(self):
        """Verifică afișarea corectă a produselor salvate în pagina /favorite/."""
        self.client.login(username='cumpărător_test', password='parola_client')
        Favorit.objects.create(utilizator=self.client_user, produs=self.produs_stoc)

        raspuns = self.client.get(reverse('cumparaturi:lista_favorite'))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "Boxă JBL Go")
        self.assertTemplateUsed(raspuns, 'cumparaturi/favorite.html')

    def test_eliminare_favorit_direct(self):
        """Verifică ștergerea directă a unui articol din favorite."""
        self.client.login(username='cumpărător_test', password='parola_client')
        fav = Favorit.objects.create(utilizator=self.client_user, produs=self.produs_stoc)

        raspuns = self.client.post(reverse('cumparaturi:elimina_favorit', kwargs={'favorit_id': fav.id}))
        self.assertRedirects(raspuns, reverse('cumparaturi:lista_favorite'))
        self.assertFalse(Favorit.objects.filter(id=fav.id).exists())

    def test_muta_in_cos_produs_in_stoc(self):
        """Verifică că 'Mută în coș' creează ArticolCos și elimină din Favorit."""
        self.client.login(username='cumpărător_test', password='parola_client')
        fav = Favorit.objects.create(utilizator=self.client_user, produs=self.produs_stoc)

        raspuns = self.client.post(reverse('cumparaturi:muta_in_cos', kwargs={'favorit_id': fav.id}))
        self.assertRedirects(raspuns, reverse('cumparaturi:lista_favorite'))

        # Verificăm că a apărut în coș
        self.assertTrue(ArticolCos.objects.filter(utilizator=self.client_user, produs=self.produs_stoc).exists())
        # Verificăm că a dispărut din favorite
        self.assertFalse(Favorit.objects.filter(id=fav.id).exists())

    def test_muta_in_cos_produs_epuizat_esueaza(self):
        """Verifică refuzul mutării în coș dacă produsul are stoc 0."""
        self.client.login(username='cumpărător_test', password='parola_client')
        fav = Favorit.objects.create(utilizator=self.client_user, produs=self.produs_epuizat)

        raspuns = self.client.post(reverse('cumparaturi:muta_in_cos', kwargs={'favorit_id': fav.id}))
        self.assertRedirects(raspuns, reverse('cumparaturi:lista_favorite'))

        # Produsul NU trebuie să apară în coș
        self.assertFalse(ArticolCos.objects.filter(utilizator=self.client_user, produs=self.produs_epuizat).exists())
        # Produsul rămâne în favorite
        self.assertTrue(Favorit.objects.filter(id=fav.id).exists())
