"""
catalog/tests.py

Teste automate pentru catalogul de produse.
În Faza 0 se testează disponibilitatea paginii principale (Acasă)
și încărcarea corectă a șablonului de bază.
"""

from django.test import TestCase
from django.urls import reverse


class PaginaPrincipalaTest(TestCase):
    """Teste de fum (smoke tests) pentru verificarea disponibilității paginii de start."""

    def test_pagina_acasa_este_disponibila(self):
        """Verifică dacă ruta principală '/' răspunde cu codul HTTP 200 OK."""
        # Pasul 1: Trimitem o cerere GET către adresa paginii de start
        raspuns = self.client.get(reverse('catalog:acasa'))

        # Pasul 2: Verificăm că pagina a răspuns cu succes
        self.assertEqual(raspuns.status_code, 200)

        # Pasul 3: Verificăm dacă template-urile așteptate au fost utilizate
        self.assertTemplateUsed(raspuns, 'catalog/acasa.html')
        self.assertTemplateUsed(raspuns, 'baza.html')

        # Pasul 4: Verificăm prezența titlului în corpul paginii
        self.assertContains(raspuns, 'ElectroMag')
        self.assertContains(raspuns, 'Bun venit la Magazinul Online')
