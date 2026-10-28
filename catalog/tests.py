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
"""

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from catalog.models import Categorie, Furnizor, ModalitateLivrare, Produs


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
        # Verificare pe pagina de produse
        raspuns_lista = self.client.get(reverse('catalog:lista_produse'))
        self.assertContains(raspuns_lista, "Laptop ASUS ZenBook")
        self.assertContains(raspuns_lista, "Căști Sony Noise Cancelling")
        self.assertNotContains(raspuns_lista, "Laptop Vechi Retras")

        # Verificare pe pagina Acasă
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
        # Căutare după nume
        raspuns_nume = self.client.get(reverse('catalog:lista_produse') + '?q=ZenBook')
        self.assertContains(raspuns_nume, "Laptop ASUS ZenBook")
        self.assertNotContains(raspuns_nume, "Căști Sony")

        # Căutare după descriere
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
        # Specificații tabel
        self.assertContains(raspuns, "OLED 14 inch")
        self.assertContains(raspuns, "Intel i5")
