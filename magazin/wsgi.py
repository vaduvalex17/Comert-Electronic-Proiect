"""
magazin/wsgi.py

Configurația WSGI pentru proiectul magazin.
Expune variabila `application` folosită de serverele web conforme WSGI
pentru a deservi aplicația în medii de producție sau la rulare sincronă.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magazin.settings')

application = get_wsgi_application()
