#!/usr/bin/env python
"""
manage.py

Utilitarul principal de linie de comandă pentru administrarea proiectului Django.
Permite rularea serverului de dezvoltare, aplicarea migrărilor, crearea
de aplicații noi și executarea testelor automate.
"""
import os
import sys


def main():
    """Rulează sarcinile administrative primite din linia de comandă."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magazin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Nu s-a putut importa Django. Verifică dacă mediul virtual este activat "
            "și dacă pachetele din requirements.txt sunt instalate."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
