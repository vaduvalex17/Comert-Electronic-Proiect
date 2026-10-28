"""
magazin/urls.py

„Cuprinsul” central al adreselor magazinului online.
Aici legăm fiecare secțiune din site de aplicația responsabilă:
- /conturi/          -> conturi (login, înregistrare, roluri)
- /favorite/, /cos/, /comanda/, /comenzi/ -> cumpărături (favorite, coș, checkout, comenzi)
- /, /produse/, /categorie/, /produs/    -> catalog (produse, categorii, CRUD admin)
- /admin/            -> panoul de administrare nativ Django
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Panoul de administrare Django (folosit pentru demo tehnic)
    path('admin/', admin.site.urls),

    # Aplicația de autentificare și roluri
    path('conturi/', include('conturi.urls', namespace='conturi')),

    # Aplicația pentru coș, favorite, checkout și comenzi (URL-uri de nivel 1 conform §5)
    path('', include('cumparaturi.urls', namespace='cumparaturi')),

    # Catalogul de produse (rutele principale: /, /produse/, /produs/<slug>/ etc.)
    path('', include('catalog.urls', namespace='catalog')),
]

# În modul de depanare (DEBUG), servim imaginile încărcate (media) prin serverul Django
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
