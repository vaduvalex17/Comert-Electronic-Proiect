"""
magazin/asgi.py

Configurația ASGI pentru proiectul magazin.
Expune variabila `application` folosită de serverele web conforme ASGI
pentru deservirea cererilor asincrone sau a conexiunilor WebSocket.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magazin.settings')

application = get_asgi_application()
