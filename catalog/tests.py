"""
catalog/tests.py

Teste automate pentru catalogul de produse:
- Disponibilitatea paginii principale (Acasă)
- Testarea funcției specificatii_lista() de transformare text -> listă
- Generarea automată a slug-ului pentru URL-uri lizibile
- Validarea prețului și stocului (valori pozitive)
- Proprietățile de calcul al stocului (in_stoc, stare_stoc)
- Vizibilitatea produselor: produsele inactive NU apar în catalog și dau 404 pe pagina de detaliu
- Filtrarea după categorie (Cerința R1.4)
- Căutarea după cuvinte cheie (Cerința R1.4)
- Pagina de detaliu produs cu toate atributele cerute (Cerința R1.3)
- Panoul de administrare CRUD produse (Cerința R1.2): adăugare, editare, ștergere fizică și soft-delete
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from catalog.models import Categorie, Furnizor, ModalitateLivrare, Produs
from cumparaturi.models import ArticolComanda, Comanda

User = get_user_model()


class PaginaPrincipalaTest(TestCase):
    """Teste de fum pentru verificarea disponibilității paginii de start."""

    def test_pagina_acasa_este_disponibila(self):
        """Verifică dacă ruta principală '/' răspunde cu codul HTTP 200 OK."""
        raspuns = self.client.get(reverse('catalog:acasa'))
        self.assertEqual(raspuns.status_code, 200)
        self.assertTemplateUsed(raspuns, 'catalog/acasa.html')
        self.assertTemplateUsed(raspuns, 'baza.html')
        self.assertContains(raspuns, 'ElectroMag')


class ModeleCatalogTest(TestCase):
    """Teste unitare pentru logica modelelor din catalog (Categorie, Produs etc.)."""

    def setUp(self):
        """Pregătește datele de bază necesare fiecărui test."""
        self.categorie = Categorie.objects.create(
            nume="Laptopuri Test",
            descriere="Descriere categorie de test"
        )
        self.furnizor = Furnizor.objects.create(
            nume="Distribuitor Test SRL",
            email="test@distribuitor.ro",
            telefon="0711222333"
        )
        self.livrare = ModalitateLivrare.objects.create(
            nume="Curier Test",
            cost=Decimal("15.00"),
            zile_estimate=1
        )

    def test_generare_automata_slug_categorie(self):
        """Verifică dacă slug-ul categoriei este generat automat din nume."""
        self.assertEqual(self.categorie.slug, "laptopuri-test")

    def test_generare_automata_slug_produs(self):
        """Verifică dacă slug-ul produsului se creează automat la salvare."""
        produs = Produs.objects.create(
            nume="Laptop Gaming Asus ROG",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("4500.00"),
            stoc=10,
            descriere="Un laptop foarte performant."
        )
        self.assertEqual(produs.slug, "laptop-gaming-asus-rog")

    def test_evitare_coliziune_slug_produse_identice(self):
        """Verifică dacă două produse cu același nume primesc slug-uri unice."""
        p1 = Produs.objects.create(
            nume="Căști Wireless Pro",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("200.00"),
            stoc=5
        )
        p2 = Produs.objects.create(
            nume="Căști Wireless Pro",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("250.00"),
            stoc=3
        )
        self.assertEqual(p1.slug, "casti-wireless-pro")
        self.assertEqual(p2.slug, "casti-wireless-pro-1")

    def test_specificatii_lista_transformare_corecta(self):
        """Verifică parsarea specificațiilor din text pe rânduri în perechi cheie-valoare."""
        produs = Produs.objects.create(
            nume="Laptop Detaliat",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("3000.00"),
            stoc=4,
            specificatii="Procesor: Intel i7\nMemorie RAM: 16 GB\nStocare: 512 GB SSD"
        )
        rezultat = produs.specificatii_lista()
        asteptat = [
            ("Procesor", "Intel i7"),
            ("Memorie RAM", "16 GB"),
            ("Stocare", "512 GB SSD")
        ]
        self.assertEqual(rezultat, asteptat)

    def test_specificatii_lista_cand_este_gol(self):
        """Verifică faptul că specificatii_lista() returnează o listă goală dacă nu există text."""
        produs = Produs.objects.create(
            nume="Produs Fără Specificații",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("100.00"),
            stoc=2,
            specificatii=""
        )
        self.assertEqual(produs.specificatii_lista(), [])

    def test_proprietati_stoc_disponibil_si_etichete(self):
        """Verifică calculul proprietăților in_stoc și stare_stoc."""
        p_stoc_normal = Produs.objects.create(
            nume="Produs Stoc Mare",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("50.00"),
            stoc=10
        )
        p_stoc_limitat = Produs.objects.create(
            nume="Produs Stoc Limitat",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("50.00"),
            stoc=3
        )
        p_indisponibil = Produs.objects.create(
            nume="Produs Epuizat",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("50.00"),
            stoc=0
        )

        self.assertTrue(p_stoc_normal.in_stoc)
        self.assertEqual(p_stoc_normal.stare_stoc, "În stoc")

        self.assertTrue(p_stoc_limitat.in_stoc)
        self.assertEqual(p_stoc_limitat.stare_stoc, "Stoc limitat")

        self.assertFalse(p_indisponibil.in_stoc)
        self.assertEqual(p_indisponibil.stare_stoc, "Indisponibil")

    def test_validator_pret_strict_pozitiv(self):
        """Verifică că validatorul respinge un preț egal cu 0 sau negativ."""
        produs_invalid = Produs(
            nume="Produs Gratuit Invalid",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("0.00"),
            stoc=5
        )
        with self.assertRaises(ValidationError):
            produs_invalid.full_clean()

    def test_validator_stoc_nenegativ(self):
        """Verifică că validatorul respinge stocurile negative."""
        produs_invalid = Produs(
            nume="Produs Stoc Negativ",
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal("10.00"),
            stoc=-1
        )
        with self.assertRaises(ValidationError):
            produs_invalid.full_clean()


class CatalogPublicTest(TestCase):
    """Teste pentru funcționalitățile publice: afișare, căutare, categorii, detaliu (R1.3, R1.4)."""

    def setUp(self):
        """Creează produse active și inactive în diferite categorii."""
        self.cat_laptop = Categorie.objects.create(nume="Laptopuri", slug="laptopuri")
        self.cat_audio = Categorie.objects.create(nume="Audio", slug="audio")

        self.furnizor = Furnizor.objects.create(
            nume="Distrib SRL",
            email="office@distrib.ro",
            telefon="0700000000"
        )
        self.livrare = ModalitateLivrare.objects.create(
            nume="Curier Rapid",
            cost=Decimal("20.00"),
            zile_estimate=1
        )

        # Produs activ categoria Laptopuri
        self.p_activ = Produs.objects.create(
            nume="Laptop ASUS ZenBook",
            slug="laptop-asus-zenbook",
            categorie=self.cat_laptop,
            furnizor=self.furnizor,
            pret=Decimal("4200.00"),
            stoc=7,
            descriere="Ultraportabil premium din aluminiu.",
            specificatii="Ecran: OLED 14 inch\nProcesor: Intel i5",
            activ=True
        )
        self.p_activ.modalitati_livrare.add(self.livrare)

        # Produs inactiv categoria Laptopuri
        self.p_inactiv = Produs.objects.create(
            nume="Laptop Vechi Retras",
            slug="laptop-vechi-retras",
            categorie=self.cat_laptop,
            furnizor=self.furnizor,
            pret=Decimal("1500.00"),
            stoc=0,
            descriere="Produs retras din vânzare.",
            activ=False
        )

        # Produs activ categoria Audio
        self.p_audio = Produs.objects.create(
            nume="Căști Sony Noise Cancelling",
            slug="casti-sony-noise-cancelling",
            categorie=self.cat_audio,
            furnizor=self.furnizor,
            pret=Decimal("899.00"),
            stoc=12,
            descriere="Sunet clar și izolare impecabilă.",
            specificatii="Autonomie: 30 ore\nConectivitate: Bluetooth",
            activ=True
        )
        self.p_audio.modalitati_livrare.add(self.livrare)

    def test_produsele_inactive_nu_apar_in_lista_sau_acasa(self):
        """Asigură că doar produsele active (activ=True) sunt afișate cumpărătorilor."""
        raspuns_lista = self.client.get(reverse('catalog:lista_produse'))
        self.assertContains(raspuns_lista, "Laptop ASUS ZenBook")
        self.assertContains(raspuns_lista, "Căști Sony Noise Cancelling")
        self.assertNotContains(raspuns_lista, "Laptop Vechi Retras")

        raspuns_acasa = self.client.get(reverse('catalog:acasa'))
        self.assertContains(raspuns_acasa, "Laptop ASUS ZenBook")
        self.assertNotContains(raspuns_acasa, "Laptop Vechi Retras")

    def test_produs_inactiv_returneaza_404_la_detaliu(self):
        """Încercarea de a accesa pagina unui produs retras/inactiv trebuie să returneze 404."""
        raspuns = self.client.get(reverse('catalog:detaliu_produs', kwargs={'slug': 'laptop-vechi-retras'}))
        self.assertEqual(raspuns.status_code, 404)

    def test_filtrare_produse_dupa_categorie(self):
        """Verifică că pagina categoriei afișează doar produsele din acea categorie (R1.4)."""
        raspuns = self.client.get(reverse('catalog:produse_categorie', kwargs={'slug': 'audio'}))
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "Căști Sony Noise Cancelling")
        self.assertNotContains(raspuns, "Laptop ASUS ZenBook")

    def test_cautare_produse_dupa_nume_si_descriere(self):
        """Verifică căutarea ?q= returnează produsele potrivite după nume sau descriere (R1.4)."""
        raspuns_nume = self.client.get(reverse('catalog:lista_produse') + '?q=ZenBook')
        self.assertContains(raspuns_nume, "Laptop ASUS ZenBook")
        self.assertNotContains(raspuns_nume, "Căști Sony")

        raspuns_desc = self.client.get(reverse('catalog:lista_produse') + '?q=izolare')
        self.assertContains(raspuns_desc, "Căști Sony Noise Cancelling")
        self.assertNotContains(raspuns_desc, "Laptop ASUS ZenBook")

    def test_detaliu_produs_contine_toate_campurile_r13(self):
        """Verifică prezența tuturor câmpurilor obligatorii cerute de R1.3 pe pagina produsului."""
        raspuns = self.client.get(reverse('catalog:detaliu_produs', kwargs={'slug': 'laptop-asus-zenbook'}))
        self.assertEqual(raspuns.status_code, 200)

        # R1.3: nume, descriere, specificații, preț, stoc, furnizor, modalitate livrare, categorie
        self.assertContains(raspuns, "Laptop ASUS ZenBook")
        self.assertContains(raspuns, "Ultraportabil premium din aluminiu.")
        self.assertContains(raspuns, "4200")
        self.assertContains(raspuns, "În stoc")
        self.assertContains(raspuns, "Distrib SRL")
        self.assertContains(raspuns, "Curier Rapid")
        self.assertContains(raspuns, "Laptopuri")
        self.assertContains(raspuns, "OLED 14 inch")
        self.assertContains(raspuns, "Intel i5")


class AdminProduseCRUDTest(TestCase):
    """Teste complete pentru panoul de administrare produse (Cerința R1.2)."""

    def setUp(self):
        """Configurează utilizatorii și datele de catalog."""
        self.admin = User.objects.create_user(
            username='admin_boss',
            password='parola_admin',
            is_staff=True
        )
        self.client_user = User.objects.create_user(
            username='client_simplu',
            password='parola_client',
            is_staff=False
        )

        self.categorie = Categorie.objects.create(nume="Tablete", slug="tablete")
        self.furnizor = Furnizor.objects.create(
            nume="Furnizor Tablete SRL",
            email="tablete@distrib.ro",
            telefon="0711000999"
        )
        self.livrare = ModalitateLivrare.objects.create(
            nume="Easybox",
            cost=Decimal("12.00")
        )

    def test_client_neautorizat_este_redirectionat(self):
        """Un client fără rol de admin nu poate accesa panoul de administrare produse."""
        self.client.login(username='client_simplu', password='parola_client')
        raspuns = self.client.get(reverse('catalog:admin_produse_lista'))
        self.assertRedirects(raspuns, reverse('catalog:acasa'))

    def test_admin_acceseaza_lista_produse(self):
        """Un admin autentificat poate vedea tabelul de administrare produse."""
        self.client.login(username='admin_boss', password='parola_admin')
        raspuns = self.client.get(reverse('catalog:admin_produse_lista'))
        self.assertEqual(raspuns.status_code, 200)
        self.assertTemplateUsed(raspuns, 'catalog/admin/admin_produse_lista.html')

    def test_admin_adauga_produs_cu_succes(self):
        """Adminul poate adăuga un produs nou prin formularul POST (R1.2)."""
        self.client.login(username='admin_boss', password='parola_admin')
        date_produs = {
            'nume': 'iPad Mini 6',
            'categorie': self.categorie.id,
            'furnizor': self.furnizor.id,
            'modalitati_livrare': [self.livrare.id],
            'pret': '2899.00',
            'stoc': 15,
            'descriere': 'Cea mai compactă tabletă performantă.',
            'specificatii': 'Ecran: 8.3 inch\nCip: A15 Bionic',
            'activ': True,
        }
        raspuns = self.client.post(reverse('catalog:admin_produs_adauga'), date_produs)
        self.assertRedirects(raspuns, reverse('catalog:admin_produse_lista'))

        # Verificăm salvarea în baza de date
        self.assertTrue(Produs.objects.filter(nume='iPad Mini 6').exists())
        produs = Produs.objects.get(nume='iPad Mini 6')
        self.assertEqual(produs.pret, Decimal('2899.00'))
        self.assertEqual(produs.stoc, 15)
        self.assertEqual(produs.modalitati_livrare.count(), 1)

    def test_admin_editeaza_produs_cu_succes(self):
        """Adminul poate actualiza datele unui produs existent (R1.2)."""
        self.client.login(username='admin_boss', password='parola_admin')
        produs = Produs.objects.create(
            nume='Tabletă De Modificat',
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal('1000.00'),
            stoc=5,
            descriere='Descriere veche.'
        )
        produs.modalitati_livrare.add(self.livrare)

        date_modificate = {
            'nume': 'Tabletă Modificată',
            'categorie': self.categorie.id,
            'furnizor': self.furnizor.id,
            'modalitati_livrare': [self.livrare.id],
            'pret': '1199.99',
            'stoc': 20,
            'descriere': 'Descriere nouă și îmbunătățită.',
            'specificatii': 'RAM: 4 GB',
            'activ': True,
        }
        raspuns = self.client.post(reverse('catalog:admin_produs_editeaza', kwargs={'pk': produs.pk}), date_modificate)
        self.assertRedirects(raspuns, reverse('catalog:admin_produse_lista'))

        produs.refresh_from_db()
        self.assertEqual(produs.nume, 'Tabletă Modificată')
        self.assertEqual(produs.pret, Decimal('1199.99'))
        self.assertEqual(produs.stoc, 20)

    def test_stergere_definitiva_cand_nu_exista_comenzi(self):
        """Dacă un produs nu a fost comandat, este șters definitiv din baza de date."""
        self.client.login(username='admin_boss', password='parola_admin')
        produs = Produs.objects.create(
            nume='Produs Fără Comenzi',
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal('500.00'),
            stoc=3
        )
        produs_id = produs.id

        raspuns = self.client.post(reverse('catalog:admin_produs_sterge', kwargs={'pk': produs_id}))
        self.assertRedirects(raspuns, reverse('catalog:admin_produse_lista'))
        # Produsul nu mai trebuie să existe în baza de date
        self.assertFalse(Produs.objects.filter(id=produs_id).exists())

    def test_soft_delete_cand_produsul_are_comenzi(self):
        """Dacă un produs apare în comenzi finalizate, NU se șterge fizic, ci se marchează activ=False."""
        self.client.login(username='admin_boss', password='parola_admin')
        produs = Produs.objects.create(
            nume='Produs Cu Istoric Comenzi',
            categorie=self.categorie,
            furnizor=self.furnizor,
            pret=Decimal('750.00'),
            stoc=2,
            activ=True
        )

        # Creăm o comandă fictivă care conține acest produs
        comanda = Comanda.objects.create(
            utilizator=self.client_user,
            nume_destinatar='Vasile Vasile',
            telefon='0722111222',
            adresa='Strada Mare 10',
            oras='Iași',
            judet='Iași',
            cod_postal='700000',
            modalitate_livrare=self.livrare,
            cost_livrare=self.livrare.cost,
            subtotal=Decimal('750.00'),
            total=Decimal('762.00')
        )
        ArticolComanda.objects.create(
            comanda=comanda,
            produs=produs,
            nume_produs=produs.nume,
            pret_unitar=produs.pret,
            cantitate=1
        )

        # Adminul cere ștergerea
        raspuns = self.client.post(reverse('catalog:admin_produs_sterge', kwargs={'pk': produs.id}))
        self.assertRedirects(raspuns, reverse('catalog:admin_produse_lista'))

        # Verificăm regula de integritate: produsul încă există în DB, dar este inactiv
        produs.refresh_from_db()
        self.assertTrue(Produs.objects.filter(id=produs.id).exists())
        self.assertFalse(produs.activ, "Produsul trebuia marcat activ=False (soft-delete)!")
