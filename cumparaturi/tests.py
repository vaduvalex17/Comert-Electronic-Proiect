"""
cumparaturi/tests.py

Teste automate pentru modulul de cumpărături:
- Modele: calcul subtotal coș, calcul subtotal linie comandă, unicități și snapshot-uri
- Favorite (Cerința R2.1): acces restricționat pentru anonimi, toggle adăugare/eliminare,
  ștergere directă din listă, mutare în coș pentru produse în stoc și verificare stoc epuizat.
- Coș de cumpărături (Cerința R2.2):
  - Calcule: subtotal, cost transport și total general
  - Plafonare cantitate la stocul disponibil
  - Intersecția modalităților de livrare (doar cele comune tuturor produselor)
  - Actualizare cantitate și eliminare din coș
- Finalizare comandă (Cerința R2.2):
  - Comandă reușită: tranzacție atomică, scădere stoc, golire coș, snapshot prețuri, total corect
  - Stoc insuficient: tranzacție anulată integral (rollback), nimic salvat
  - Validare card Luhn și respingerea cardurilor expirate
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from catalog.models import Categorie, Furnizor, ModalitateLivrare, Produs
from cumparaturi.models import ArticolComanda, ArticolCos, CodReducere, Comanda, Favorit

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

        self.client.post(reverse('cumparaturi:adauga_elimina_favorit', kwargs={'produs_id': self.produs_stoc.id}))
        self.assertTrue(Favorit.objects.filter(utilizator=self.client_user, produs=self.produs_stoc).exists())

        self.client.post(reverse('cumparaturi:adauga_elimina_favorit', kwargs={'produs_id': self.produs_stoc.id}))
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
        self.assertRedirects(raspuns, reverse('cumparaturi:vizualizare_cos'))

        self.assertTrue(ArticolCos.objects.filter(utilizator=self.client_user, produs=self.produs_stoc).exists())
        self.assertFalse(Favorit.objects.filter(id=fav.id).exists())

    def test_muta_in_cos_produs_epuizat_esueaza(self):
        """Verifică refuzul mutării în coș dacă produsul are stoc 0."""
        self.client.login(username='cumpărător_test', password='parola_client')
        fav = Favorit.objects.create(utilizator=self.client_user, produs=self.produs_epuizat)

        raspuns = self.client.post(reverse('cumparaturi:muta_in_cos', kwargs={'favorit_id': fav.id}))
        self.assertRedirects(raspuns, reverse('cumparaturi:lista_favorite'))

        self.assertFalse(ArticolCos.objects.filter(utilizator=self.client_user, produs=self.produs_epuizat).exists())
        self.assertTrue(Favorit.objects.filter(id=fav.id).exists())


class CosCumparaturiTest(TestCase):
    """Teste complete pentru coșul de cumpărături, stocuri și livrări (Cerința R2.2)."""

    def setUp(self):
        """Pregătește utilizatori, produse și modalități diferite de livrare."""
        self.client_user = User.objects.create_user(
            username='cumparator_cos',
            password='parola_cos'
        )
        self.cat = Categorie.objects.create(nume='Laptopuri', slug='laptopuri')
        self.furnizor = Furnizor.objects.create(
            nume='Furnizor IT',
            email='it@furnizor.ro',
            telefon='0711999888'
        )

        self.livrare_curier = ModalitateLivrare.objects.create(
            nume='Curier Rapid',
            cost=Decimal('20.00'),
            zile_estimate=1
        )
        self.livrare_easybox = ModalitateLivrare.objects.create(
            nume='Easybox',
            cost=Decimal('10.00'),
            zile_estimate=2
        )
        self.livrare_showroom = ModalitateLivrare.objects.create(
            nume='Showroom',
            cost=Decimal('0.00'),
            zile_estimate=1
        )

        self.p1 = Produs.objects.create(
            nume='Laptop Dell Inspiron',
            slug='laptop-dell-inspiron',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('3000.00'),
            stoc=3,
            activ=True
        )
        self.p1.modalitati_livrare.add(self.livrare_curier, self.livrare_easybox)

        self.p2 = Produs.objects.create(
            nume='Mouse Wireless',
            slug='mouse-wireless',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('100.00'),
            stoc=10,
            activ=True
        )
        self.p2.modalitati_livrare.add(self.livrare_curier, self.livrare_showroom)

    def test_acces_cos_necesita_autentificare(self):
        """Un vizitator anonim este redirecționat la login dacă accesează /cos/."""
        raspuns = self.client.get(reverse('cumparaturi:vizualizare_cos'))
        self.assertRedirects(raspuns, f"{reverse('conturi:login')}?next={reverse('cumparaturi:vizualizare_cos')}")

    def test_adaugare_in_cos_produs_in_stoc(self):
        """Adăugarea prin POST creează un ArticolCos sau incrementează cantitatea."""
        self.client.login(username='cumparator_cos', password='parola_cos')

        raspuns1 = self.client.post(reverse('cumparaturi:adaugare_in_cos', kwargs={'produs_id': self.p1.id}), {'cantitate': 1})
        self.assertRedirects(raspuns1, reverse('cumparaturi:vizualizare_cos'))

        articol = ArticolCos.objects.get(utilizator=self.client_user, produs=self.p1)
        self.assertEqual(articol.cantitate, 1)

        self.client.post(reverse('cumparaturi:adaugare_in_cos', kwargs={'produs_id': self.p1.id}), {'cantitate': 1})
        articol.refresh_from_db()
        self.assertEqual(articol.cantitate, 2)

    def test_plafonare_cantitate_la_stocul_disponibil(self):
        """Dacă utilizatorul cere o cantitate mai mare decât stocul (stoc=3), este plafonat la 3."""
        self.client.login(username='cumparator_cos', password='parola_cos')

        self.client.post(reverse('cumparaturi:adaugare_in_cos', kwargs={'produs_id': self.p1.id}), {'cantitate': 5})
        articol = ArticolCos.objects.get(utilizator=self.client_user, produs=self.p1)
        self.assertEqual(articol.cantitate, 3)

    def test_actualizare_cantitate_si_eliminare_la_zero(self):
        """Modificarea cantității din coș: actualizare la valoare validă sau ștergere la cantitate 0."""
        self.client.login(username='cumparator_cos', password='parola_cos')
        articol = ArticolCos.objects.create(utilizator=self.client_user, produs=self.p1, cantitate=1)

        self.client.post(reverse('cumparaturi:actualizeaza_cos', kwargs={'articol_id': articol.id}), {'cantitate': 2})
        articol.refresh_from_db()
        self.assertEqual(articol.cantitate, 2)

        self.client.post(reverse('cumparaturi:actualizeaza_cos', kwargs={'articol_id': articol.id}), {'cantitate': 0})
        self.assertFalse(ArticolCos.objects.filter(id=articol.id).exists())

    def test_calcul_subtotal_si_total_cu_livrare(self):
        """Verifică corectitudinea calculului subtotalului și a totalului pe pagina de coș."""
        self.client.login(username='cumparator_cos', password='parola_cos')

        ArticolCos.objects.create(utilizator=self.client_user, produs=self.p1, cantitate=2)
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.p2, cantitate=1)

        raspuns = self.client.get(reverse('cumparaturi:vizualizare_cos'))
        self.assertEqual(raspuns.status_code, 200)
        self.assertEqual(raspuns.context['subtotal'], Decimal('6100.00'))
        self.assertEqual(raspuns.context['cost_livrare'], Decimal('20.00'))
        self.assertEqual(raspuns.context['total'], Decimal('6120.00'))

    def test_intersectia_modalitatilor_de_livrare(self):
        """Verifică regula §6.1: doar opțiunile comune TUTUROR produselor din coș sunt oferite."""
        self.client.login(username='cumparator_cos', password='parola_cos')

        ArticolCos.objects.create(utilizator=self.client_user, produs=self.p1, cantitate=1)
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.p2, cantitate=1)

        raspuns = self.client.get(reverse('cumparaturi:vizualizare_cos'))
        livrari_oferite = raspuns.context['livrari_comune']
        self.assertEqual(len(livrari_oferite), 1)
        self.assertEqual(livrari_oferite[0].nume, 'Curier Rapid')


class FinalizareComandaTest(TestCase):
    """Teste complete pentru procesul de checkout și plasare a comenzii (Cerința R2.2)."""

    def setUp(self):
        """Configurează clientul, produsul și modalitatea de livrare."""
        self.client_user = User.objects.create_user(
            username='client_checkout',
            password='parola_client',
            first_name='Mihai',
            last_name='Ionescu'
        )
        self.cat = Categorie.objects.create(nume='Telefoane', slug='telefoane')
        self.furnizor = Furnizor.objects.create(
            nume='Furnizor GSM SRL',
            email='gsm@furnizor.ro',
            telefon='0788111222'
        )
        self.livrare = ModalitateLivrare.objects.create(
            nume='Curier Express',
            cost=Decimal('25.00'),
            zile_estimate=1
        )
        self.produs = Produs.objects.create(
            nume='Smartphone Galaxy S24',
            slug='smartphone-galaxy-s24',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('4000.00'),
            stoc=5,
            activ=True
        )
        self.produs.modalitati_livrare.add(self.livrare)

        # Date valide de checkout (card de test Visa cu algoritm Luhn valid)
        self.date_checkout_valide = {
            'nume_destinatar': 'Mihai Ionescu',
            'telefon': '0722123456',
            'adresa': 'Strada Teilor nr. 5',
            'oras': 'Cluj-Napoca',
            'judet': 'Cluj',
            'cod_postal': '400001',
            'modalitate_livrare': self.livrare.id,
            'titular_card': 'MIHAI IONESCU',
            'numar_card': '4242 4242 4242 4242',  # Luhn valid
            'expirare_card': '12/28',             # În viitor
            'cvv_card': '123',                    # 3 cifre
        }

    def test_checkout_reusit_scade_stoc_goleste_cos_si_creeaza_comanda(self):
        """O comandă validă scade stocul, golește coșul, salvează comanda și snapshot-ul de preț."""
        self.client.login(username='client_checkout', password='parola_client')

        # Adăugăm 2 bucăți în coș (stocul inițial este 5)
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=2)

        # Trimitere formular checkout
        raspuns = self.client.post(reverse('cumparaturi:finalizare_comanda'), self.date_checkout_valide)

        # Verificăm că am fost redirecționați pe pagina de confirmare
        comanda = Comanda.objects.filter(utilizator=self.client_user).first()
        self.assertIsNotNone(comanda)
        self.assertRedirects(raspuns, reverse('cumparaturi:confirmare_comanda', kwargs={'comanda_id': comanda.id}))

        # 1. Stocul a scăzut de la 5 la 3
        self.produs.refresh_from_db()
        self.assertEqual(self.produs.stoc, 3)

        # 2. Coșul a fost golit complet
        self.assertEqual(ArticolCos.objects.filter(utilizator=self.client_user).count(), 0)

        # 3. Datele financiare sunt corecte (2 x 4000 = 8000 + 25 = 8025 lei)
        self.assertEqual(comanda.subtotal, Decimal('8000.00'))
        self.assertEqual(comanda.cost_livrare, Decimal('25.00'))
        self.assertEqual(comanda.total, Decimal('8025.00'))

        # 4. Securitate: din card se păstrează doar ultimele 4 cifre
        self.assertEqual(comanda.card_ultimele4, '4242')

        # 5. Snapshot linie de comandă
        self.assertEqual(comanda.articole.count(), 1)
        linie = comanda.articole.first()
        self.assertEqual(linie.nume_produs, 'Smartphone Galaxy S24')
        self.assertEqual(linie.pret_unitar, Decimal('4000.00'))
        self.assertEqual(linie.cantitate, 2)

    def test_stoc_insuficient_anuleaza_tranzactia(self):
        """Dacă stocul scade între timp și devine insuficient, comanda este respinsă și nimic nu se salvează."""
        self.client.login(username='client_checkout', password='parola_client')

        # Adăugăm 3 bucăți în coș
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=3)

        # Simulăm că alt cumpărător a cumpărat marfa și a rămas doar 1 bucată în stoc
        self.produs.stoc = 1
        self.produs.save()

        raspuns = self.client.post(reverse('cumparaturi:finalizare_comanda'), self.date_checkout_valide)

        # Nu s-a creat nicio comandă
        self.assertEqual(Comanda.objects.filter(utilizator=self.client_user).count(), 0)
        # Coșul a rămas neatins
        self.assertEqual(ArticolCos.objects.filter(utilizator=self.client_user).count(), 1)
        # Stocul a rămas 1
        self.produs.refresh_from_db()
        self.assertEqual(self.produs.stoc, 1)

    def test_card_invalid_luhn_este_respins(self):
        """Un card care nu trece algoritmul Luhn este respins la validare și nu se creează comandă."""
        self.client.login(username='client_checkout', password='parola_client')
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=1)

        date_card_gresit = self.date_checkout_valide.copy()
        date_card_gresit['numar_card'] = '4532 0000 0000 0001'  # Luhn invalid

        raspuns = self.client.post(reverse('cumparaturi:finalizare_comanda'), date_card_gresit)
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "nu trece verificarea algoritmului Luhn")
        self.assertEqual(Comanda.objects.count(), 0)

    def test_card_expirat_este_respins(self):
        """Un card cu data de expirare în trecut este respins."""
        self.client.login(username='client_checkout', password='parola_client')
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=1)

        date_card_expirat = self.date_checkout_valide.copy()
        date_card_expirat['expirare_card'] = '01/20'  # Expirat

        raspuns = self.client.post(reverse('cumparaturi:finalizare_comanda'), date_card_expirat)
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "Cardul bancar este expirat")
        self.assertEqual(Comanda.objects.count(), 0)


class IstoricSiAdministrareComenziTest(TestCase):
    """Teste pentru istoricul comenzilor (R2.3) și panoul de gestiune a comenzilor pentru admin."""

    def setUp(self):
        """Creează doi clienți și un administrator cu comenzi dedicate fiecăruia."""
        self.client_1 = User.objects.create_user(username='client1', password='parola123')
        self.client_2 = User.objects.create_user(username='client2', password='parola123')
        self.admin_user = User.objects.create_user(
            username='admin_boss',
            password='parola_admin',
            is_staff=True
        )

        self.cat = Categorie.objects.create(nume='Monitoare')
        self.furnizor = Furnizor.objects.create(nume='Tech Supplier', email='t@sup.ro', telefon='0711222333')
        self.livrare = ModalitateLivrare.objects.create(nume='Curier Prioritar', cost=Decimal('20.00'))

        self.produs = Produs.objects.create(
            nume='Monitor Gaming 144Hz',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('1200.00'),
            stoc=10
        )

        # Comanda pentru client 1
        self.comanda_1 = Comanda.objects.create(
            utilizator=self.client_1,
            modalitate_livrare=self.livrare,
            nume_destinatar='Client Unu',
            telefon='0711111111',
            adresa='Strada Unu nr. 1',
            oras='București',
            judet='București',
            cod_postal='010101',
            cost_livrare=self.livrare.cost,
            total=Decimal('1220.00'),
            card_ultimele4='4242',
            status='plasata'
        )
        ArticolComanda.objects.create(
            comanda=self.comanda_1,
            produs=self.produs,
            nume_produs=self.produs.nume,
            pret_unitar=self.produs.pret,
            cantitate=1
        )

        # Comanda pentru client 2
        self.comanda_2 = Comanda.objects.create(
            utilizator=self.client_2,
            modalitate_livrare=self.livrare,
            nume_destinatar='Client Doi',
            telefon='0722222222',
            adresa='Strada Doi nr. 2',
            oras='Cluj-Napoca',
            judet='Cluj',
            cod_postal='400100',
            cost_livrare=self.livrare.cost,
            total=Decimal('2420.00'),
            card_ultimele4='9999',
            status='in_procesare'
        )
        ArticolComanda.objects.create(
            comanda=self.comanda_2,
            produs=self.produs,
            nume_produs=self.produs.nume,
            pret_unitar=self.produs.pret,
            cantitate=2
        )

    def test_client_vede_doar_propriile_comenzi_in_istoric(self):
        """Un client vede pe /comenzi/ doar comenzile plasate din contul său (R2.3)."""
        self.client.login(username='client1', password='parola123')
        raspuns = self.client.get(reverse('cumparaturi:istoric_comenzi'))

        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, f"#{self.comanda_1.id}")
        self.assertContains(raspuns, "Client Unu")
        # Nu trebuie să vadă comanda clientului 2
        self.assertNotContains(raspuns, f"#{self.comanda_2.id}")
        self.assertNotContains(raspuns, "Client Doi")

    def test_client_poate_vedea_detaliul_propriei_comenzi(self):
        """Un client poate accesa factura propriei comenzi."""
        self.client.login(username='client1', password='parola123')
        raspuns = self.client.get(reverse('cumparaturi:detaliu_comanda', kwargs={'comanda_id': self.comanda_1.id}))

        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, f"Comanda #{self.comanda_1.id}")
        self.assertContains(raspuns, "Monitor Gaming 144Hz")
        self.assertContains(raspuns, "Card **** 4242")
        self.assertContains(raspuns, "Strada Unu nr. 1")

    def test_securitate_idor_client_nu_poate_vedea_comanda_altui_utilizator(self):
        """Securitate critică §6.2: accesul la o comandă străină prin ID în URL returnează strict 404 Not Found."""
        self.client.login(username='client1', password='parola123')
        raspuns = self.client.get(reverse('cumparaturi:detaliu_comanda', kwargs={'comanda_id': self.comanda_2.id}))

        self.assertEqual(raspuns.status_code, 404)

    def test_utilizator_neautentificat_redirectionat_la_login(self):
        """Un vizitator anonim este redirecționat la formularul de conectare."""
        raspuns = self.client.get(reverse('cumparaturi:istoric_comenzi'))
        self.assertEqual(raspuns.status_code, 302)
        self.assertIn(reverse('conturi:login'), raspuns.url)

    def test_non_staff_nu_poate_accesa_administrare_comenzi(self):
        """Un client normal fără drepturi staff este blocat la accesarea panoului admin de comenzi."""
        self.client.login(username='client1', password='parola123')
        raspuns = self.client.get(reverse('cumparaturi:admin_comenzi_lista'))
        self.assertEqual(raspuns.status_code, 302)
        self.assertRedirects(raspuns, reverse('catalog:acasa'))

    def test_admin_vede_toate_comenzile_in_panou(self):
        """Administratorul are acces la lista globală a comenzilor tuturor clienților."""
        self.client.login(username='admin_boss', password='parola_admin')
        raspuns = self.client.get(reverse('cumparaturi:admin_comenzi_lista'))

        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, f"#{self.comanda_1.id}")
        self.assertContains(raspuns, f"#{self.comanda_2.id}")
        self.assertContains(raspuns, "Client Unu")
        self.assertContains(raspuns, "Client Doi")

    def test_admin_poate_schimba_statusul_comenzii(self):
        """Administratorul poate trimite un formular POST pentru actualizarea stadiului comenzii."""
        self.client.login(username='admin_boss', password='parola_admin')
        url_status = reverse('cumparaturi:admin_comanda_status', kwargs={'comanda_id': self.comanda_1.id})

        raspuns = self.client.post(url_status, {'status': 'livrata'})
        self.assertRedirects(raspuns, reverse('cumparaturi:admin_comenzi_lista'))

        self.comanda_1.refresh_from_db()
        self.assertEqual(self.comanda_1.status, 'livrata')


class CodReducereBonusTest(TestCase):
    """Teste pentru Bonusul de Coduri Promoționale de Reducere."""

    def setUp(self):
        """Configurează clientul, produsele și codurile promoționale."""
        self.client_user = User.objects.create_user(username='client_promo', password='parola123')
        self.cat = Categorie.objects.create(nume='Accesorii')
        self.furnizor = Furnizor.objects.create(nume='Furnizor Promo', email='p@t.ro', telefon='0700111222')
        self.livrare = ModalitateLivrare.objects.create(nume='Curier', cost=Decimal('20.00'))

        self.produs = Produs.objects.create(
            nume='Tastatură Mecanică RGB',
            categorie=self.cat,
            furnizor=self.furnizor,
            pret=Decimal('500.00'),
            stoc=10
        )
        self.produs.modalitati_livrare.add(self.livrare)

        # Cod 1: 10% reducere fără prag minim
        self.cupon_10 = CodReducere.objects.create(
            cod='TEST10',
            procent_reducere=10,
            valoare_minima_comanda=Decimal('0.00'),
            activ=True
        )

        # Cod 2: 20% reducere cu prag minim de 1000 lei
        self.cupon_vip = CodReducere.objects.create(
            cod='VIP20',
            procent_reducere=20,
            valoare_minima_comanda=Decimal('1000.00'),
            activ=True
        )

    def test_salvare_cod_cu_majuscule(self):
        """Codul este salvat automat cu litere mari în baza de date."""
        cupon = CodReducere.objects.create(cod='  reducere5  ', procent_reducere=5)
        self.assertEqual(cupon.cod, 'REDUCERE5')

    def test_aplicare_cod_valid_in_cos(self):
        """Un cod valid se salvează în sesiune și scade totalul afișat în coș."""
        self.client.login(username='client_promo', password='parola123')
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=1)

        # Aplicăm TEST10 prin POST
        url_aplica = reverse('cumparaturi:aplica_cod_reducere')
        raspuns = self.client.post(url_aplica, {'cod': 'test10'})
        self.assertRedirects(raspuns, reverse('cumparaturi:vizualizare_cos'))

        # Verificăm că sesiunea a reținut codul
        self.assertEqual(self.client.session.get('cod_reducere'), 'TEST10')

        # Vizualizăm coșul: 500 lei - 10% (50 lei) + 20 livrare = 470 lei total
        raspuns_cos = self.client.get(reverse('cumparaturi:vizualizare_cos'))
        self.assertEqual(raspuns_cos.status_code, 200)
        self.assertEqual(raspuns_cos.context['valoare_reducere'], Decimal('50.00'))
        self.assertEqual(raspuns_cos.context['total'], Decimal('470.00'))

    def test_respingere_cod_sub_pragul_minim(self):
        """Un cod cu valoare minimă neatinsă este respins la aplicare."""
        self.client.login(username='client_promo', password='parola123')
        # Subtotal: 1 x 500 = 500 lei < 1000 lei (pragul pentru VIP20)
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=1)

        url_aplica = reverse('cumparaturi:aplica_cod_reducere')
        raspuns = self.client.post(url_aplica, {'cod': 'VIP20'})
        self.assertRedirects(raspuns, reverse('cumparaturi:vizualizare_cos'))

        # Sesiunea nu trebuie să rețină codul
        self.assertIsNone(self.client.session.get('cod_reducere'))

    def test_eliminare_cod_din_cos(self):
        """Utilizatorul poate elimina un cod aplicat anterior."""
        self.client.login(username='client_promo', password='parola123')
        session = self.client.session
        session['cod_reducere'] = 'TEST10'
        session.save()

        url_elimina = reverse('cumparaturi:elimina_cod_reducere')
        raspuns = self.client.post(url_elimina)
        self.assertRedirects(raspuns, reverse('cumparaturi:vizualizare_cos'))

        self.assertIsNone(self.client.session.get('cod_reducere'))

    def test_checkout_cu_cod_reducere_salveaza_reducerea_pe_comanda(self):
        """La plasarea comenzii, reducerea este calculată, salvată pe comandă și sesiunea este curățată."""
        self.client.login(username='client_promo', password='parola123')
        ArticolCos.objects.create(utilizator=self.client_user, produs=self.produs, cantitate=2)  # 2 x 500 = 1000 lei

        # Setăm codul TEST10 în sesiune (10% din 1000 = 100 lei reducere)
        session = self.client.session
        session['cod_reducere'] = 'TEST10'
        session.save()

        date_checkout = {
            'nume_destinatar': 'Ion Promo',
            'telefon': '0711222333',
            'adresa': 'Strada Promo 1',
            'oras': 'București',
            'judet': 'București',
            'cod_postal': '010101',
            'modalitate_livrare': self.livrare.id,
            'titular_card': 'ION PROMO',
            'numar_card': '4242 4242 4242 4242',
            'expirare_card': '12/28',
            'cvv_card': '123',
        }

        raspuns = self.client.post(reverse('cumparaturi:finalizare_comanda'), date_checkout)
        comanda = Comanda.objects.filter(utilizator=self.client_user).first()
        self.assertIsNotNone(comanda)
        self.assertRedirects(raspuns, reverse('cumparaturi:confirmare_comanda', kwargs={'comanda_id': comanda.id}))

        # Verificăm datele financiare pe comandă:
        # Subtotal: 1000 lei
        # Reducere: 100 lei
        # Transport: 20 lei
        # Total: (1000 - 100) + 20 = 920 lei
        self.assertEqual(comanda.subtotal, Decimal('1000.00'))
        self.assertEqual(comanda.valoare_reducere, Decimal('100.00'))
        self.assertEqual(comanda.total, Decimal('920.00'))
        self.assertEqual(comanda.cod_reducere, self.cupon_10)

        # Sesiunea nu mai are codul
        self.assertIsNone(self.client.session.get('cod_reducere'))


