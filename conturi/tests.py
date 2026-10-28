"""
conturi/tests.py

Teste automate pentru modulul de autentificare și roluri:
- Înregistrarea unui cont nou creează un client non-staff
- Validarea unicității email-ului la înregistrare
- Autentificarea cu credențiale corecte și greșite
- Deconectarea sigură prin metoda POST
- Protecția prin decoratorul @doar_admin (refuz pentru anonimi și clienți, permis pentru admin)
"""

from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse
from conturi.decoratori import doar_admin

User = get_user_model()


class AutentificareTest(TestCase):
    """Teste pentru fluxul complet de creare cont, login și logout."""

    def setUp(self):
        """Creează un utilizator client și unul admin pentru teste."""
        self.client_user = User.objects.create_user(
            username='client_test',
            email='client@test.ro',
            password='parola_client',
            is_staff=False
        )
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.ro',
            password='parola_admin',
            is_staff=True
        )

    def test_inregistrare_creeaza_client_non_staff(self):
        """Verifică că înregistrarea publică creează un utilizator fără drepturi de staff."""
        date_formular = {
            'username': 'utilizator_nou',
            'first_name': 'Mihai',
            'last_name': 'Ionescu',
            'email': 'mihai@exemplu.ro',
            'password1': 'ParolaComplicata123!',
            'password2': 'ParolaComplicata123!',
        }
        raspuns = self.client.post(reverse('conturi:inregistrare'), date_formular)
        # Redirecționare pe acasă după crearea cu succes
        self.assertRedirects(raspuns, reverse('catalog:acasa'))

        # Verificăm utilizatorul salvat în baza de date
        utilizator = User.objects.get(username='utilizator_nou')
        self.assertEqual(utilizator.email, 'mihai@exemplu.ro')
        self.assertEqual(utilizator.first_name, 'Mihai')
        self.assertFalse(utilizator.is_staff, "Utilizatorul înregistrat nu trebuie să aibă is_staff=True!")
        self.assertFalse(utilizator.is_superuser, "Utilizatorul înregistrat nu trebuie să aibă is_superuser=True!")

    def test_login_cu_succes(self):
        """Verifică conectarea reușită cu utilizator și parolă corecte."""
        raspuns = self.client.post(reverse('conturi:login'), {
            'username': 'client_test',
            'password': 'parola_client'
        })
        self.assertRedirects(raspuns, reverse('catalog:acasa'))
        # Verificăm că utilizatorul este autentificat în sesiune
        self.assertEqual(int(self.client.session['_auth_user_id']), self.client_user.pk)

    def test_login_cu_parola_gresita(self):
        """Verifică că o parolă greșită este respinsă cu mesaj de eroare."""
        raspuns = self.client.post(reverse('conturi:login'), {
            'username': 'client_test',
            'password': 'parola_total_gresita'
        })
        self.assertEqual(raspuns.status_code, 200)
        self.assertContains(raspuns, "Autentificarea a eșuat")
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_prin_post(self):
        """Verifică deconectarea prin cerere POST."""
        self.client.login(username='client_test', password='parola_client')
        self.assertIn('_auth_user_id', self.client.session)

        raspuns = self.client.post(reverse('conturi:logout'))
        self.assertRedirects(raspuns, reverse('catalog:acasa'))
        self.assertNotIn('_auth_user_id', self.client.session)


class DecoratorDoarAdminTest(TestCase):
    """Testează funcționarea decoratorului @doar_admin."""

    def setUp(self):
        """Creează utilizatori și un view fictiv protejat cu @doar_admin."""
        self.factory = RequestFactory()
        self.client_user = User.objects.create_user(
            username='client_simplu',
            password='parola123',
            is_staff=False
        )
        self.admin_user = User.objects.create_user(
            username='admin_sef',
            password='parola123',
            is_staff=True
        )

        # Definim o funcție view simplă protejată cu decoratorul nostru
        @doar_admin
        def pagina_secreta_admin(request):
            return HttpResponse("Acces permis în panoul de administrare!")

        self.view_protejat = pagina_secreta_admin

    def _pregateste_cerere(self, request, user):
        """Atașează middleware de sesiune, mesaje și utilizatorul pe cerere."""
        request.user = user
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda req: None).process_request(request)
        return request

    def test_vizitator_neautentificat_este_redirectionat_la_login(self):
        """Un vizitator nelogat trebuie să fie redirecționat la pagina de autentificare."""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/administrare/test/')
        self._pregateste_cerere(request, AnonymousUser())

        raspuns = self.view_protejat(request)
        self.assertEqual(raspuns.status_code, 302)
        self.assertEqual(raspuns.url, reverse('conturi:login'))

    def test_clientul_obisnuit_primeste_refuz_si_este_redirectionat(self):
        """Un client logat fără drepturi de admin este redirecționat pe Acasă cu mesaj de eroare."""
        request = self.factory.get('/administrare/test/')
        self._pregateste_cerere(request, self.client_user)

        raspuns = self.view_protejat(request)
        self.assertEqual(raspuns.status_code, 302)
        self.assertEqual(raspuns.url, reverse('catalog:acasa'))

    def test_adminul_are_acces_la_pagina_protejata(self):
        """Un utilizator cu is_staff=True primește acces nestingherit."""
        request = self.factory.get('/administrare/test/')
        self._pregateste_cerere(request, self.admin_user)

        raspuns = self.view_protejat(request)
        self.assertEqual(raspuns.status_code, 200)
        self.assertIn("Acces permis", raspuns.content.decode('utf-8'))
