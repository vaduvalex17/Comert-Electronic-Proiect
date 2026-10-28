"""
magazin/settings.py

Fișierul central de configurare pentru magazinul online.
Aici sunt definite:
- Aplicațiile instalate (conturi, catalog, cumparaturi)
- Conexiunea la baza de date (SQLite)
- Localizarea (limba română și fusul orar pentru București)
- Căile pentru fișiere statice (CSS/imagini) și media (poze produse)
- Paginile implicite de redirecționare pentru autentificare
"""

import os
from pathlib import Path

# Calea către rădăcina proiectului (folderul Proiect/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Cheia secretă: se citește din variabila de mediu dacă există, altfel folosește
# o cheie prestabilită pentru mediul local de dezvoltare.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-magazin-electronic-cheie-secreta-pentru-dezvoltare-locala-2026'
)

# Modul de depanare (DEBUG): pe True în dezvoltare, afișează mesaje detaliate la erori.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

# Gazdele permise pentru rulare locală
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver', '[::1]']

# Definirea aplicațiilor active în proiect
INSTALLED_APPS = [
    # Aplicații standard Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicațiile specifice magazinului nostru
    'conturi.apps.ConturiConfig',
    'catalog.apps.CatalogConfig',
    'cumparaturi.apps.CumparaturiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'magazin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Folderul global pentru template-uri comune (baza.html etc.)
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'magazin.wsgi.application'

# Baza de date SQLite: un fișier local compact și fără configurare suplimentară
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validarea parolelor pentru utilizatori
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Setări regionale (Limba română și fusul orar al României)
LANGUAGE_CODE = 'ro'
TIME_ZONE = 'Europe/Bucharest'
USE_I18N = True
USE_TZ = True

# Fișiere statice (CSS, imagini ale temei, JavaScript)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Fișiere media încărcate de utilizatori/admin (fotografii produse)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tipul implicit pentru cheile primare
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rutare pentru autentificare
LOGIN_URL = 'conturi:login'
LOGIN_REDIRECT_URL = 'catalog:acasa'
LOGOUT_REDIRECT_URL = 'catalog:acasa'
