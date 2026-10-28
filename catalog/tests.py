"""
catalog/tests.py

Teste automate pentru catalogul de produse:
- Disponibilitatea paginii principale (Acasă)
- Testarea funcției specificatii_lista() de transformare text -> listă
- Generarea automată a slug-ului pentru URL-uri lizibile
- Validarea prețului și stocului (valori pozitive)
- Proprietățile de calcul al stocului (in_stoc, stare_stoc)
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
        # Pasul 1: Creăm categoria de test
        self.categorie = Categorie.objects.create(
            nume="Laptopuri Test",
            descriere="Descriere categorie de test"
        )
        # Pasul 2: Creăm furnizorul de test
        self.furnizor = Furnizor.objects.create(
            nume="Distribuitor Test SRL",
            email="test@distribuitor.ro",
            telefon="0711222333"
        )
        # Pasul 3: Creăm modalitatea de livrare de test
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
