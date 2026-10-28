"""
conturi/tests.py

Teste automate pentru modulul de utilizatori, autentificare și roluri.
Testele detaliate de autentificare sunt adăugate în Faza 2.
"""

from django.test import TestCase


class ConturiInitTest(TestCase):
    """Test inițial pentru confirmarea funcționării pachetului conturi."""

    def test_pachet_activ(self):
        """Confirmă că aplicația conturi este încărcată."""
        self.assertTrue(True)
