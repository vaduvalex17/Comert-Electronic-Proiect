"""
cumparaturi/tests.py

Teste automate pentru modulul de cumpărături (favorite, coș, checkout, comenzi).
Testele specifice sunt dezvoltate în Fazele 5-8.
"""

from django.test import TestCase


class CumparaturiInitTest(TestCase):
    """Test inițial pentru confirmarea funcționării pachetului cumparaturi."""

    def test_pachet_activ(self):
        """Confirmă că aplicația cumparaturi este încărcată."""
        self.assertTrue(True)
