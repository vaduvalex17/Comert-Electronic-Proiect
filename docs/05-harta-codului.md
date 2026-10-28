# 05. Harta Codului Sursă

**„Vreau să găsesc X în cod, unde mă uit?”**
Tabelul de mai jos mapează fiecare funcționalitate pe fișierele și funcțiile corespunzătoare.

---

## 1. Index funcționalități

| Funcționalitate | Unde se află fișierul | Funcție / Element | Descriere scurtă |
|---|---|---|---|
| **Pornire & Configurare** | `magazin/settings.py` | Configurații generale | Setări aplicații, limbă, căi statice |
| **Cuprins URL-uri** | `magazin/urls.py` | `urlpatterns` | Direcționarea adreselor web |
| **Pagina Acasă** | `catalog/views.py` | `acasa()` | Afișare pagină principală |
| **Șablon de bază (HTML)** | `templates/baza.html` | Schelet HTML | Meniu, Bootstrap, mesaje flash, subsol |
| **Stiluri CSS proprii** | `static/css/stil.css` | Reguli CSS | Ajustări vizuale peste Bootstrap |
| **Modele Catalog (R1.3)** | `catalog/models.py` | `Produs`, `Categorie`, `Furnizor`, `ModalitateLivrare` | Baza de date pentru catalogul de produse |
| **Parsare specificații** | `catalog/models.py` | `Produs.specificatii_lista()` | Transformă textul de specificații în tabel |
| **Modele Cumpărături (R2.x)**| `cumparaturi/models.py` | `Favorit`, `ArticolCos`, `Comanda`, `ArticolComanda` | Baza de date pentru coș, comenzi și wishlist |
| **Comandă date demo** | `catalog/management/commands/populeaza_date.py` | `Command.handle()` | Creează conturi, categorii și 20 de produse |
| **Panou Admin Django** | `catalog/admin.py`, `cumparaturi/admin.py` | `*Admin` | Înregistrarea modelelor în `/admin/` |
| **Formulare Autentificare** | `conturi/forms.py` | `FormularInregistrare`, `FormularAutentificare` | Validare date utilizatori și clase Bootstrap |
| **Autentificare (R1.1)** | `conturi/views.py` | `login_utilizator()` | Autentificare client / admin |
| **Deconectare sigură (POST)**| `conturi/views.py` | `logout_utilizator()` | Deconectare prin POST cu token CSRF |
| **Înregistrare Client (R1.1)**| `conturi/views.py` | `inregistrare_utilizator()`| Creare cont client (non-staff) |
| **Restricție Rol Admin** | `conturi/decoratori.py` | `@doar_admin` | Blochează accesul clienților pe paginile admin |

---

## 2. Ghid rapid de orientare în proiect

1. **Vrei să modifici formularele de autentificare sau înregistrare?** Deschide `conturi/forms.py`.
2. **Vrei să vezi cum este protejată o pagină de admin?** Verifică decoratorul `@doar_admin` din `conturi/decoratori.py`.
3. **Vrei să modifici structura tabelelor sau adaugi câmpuri noi?** Deschide `catalog/models.py` sau `cumparaturi/models.py`. Nu uita să rulezi `python manage.py makemigrations` și `python manage.py migrate`.
4. **Vrei să modifici produsele din demo?** Deschide `catalog/management/commands/populeaza_date.py`.
5. **Vrei să modifici bara de meniu sau subsolul?** Deschide `templates/baza.html`.
6. **Vrei să schimbi culori sau spațieri?** Deschide `static/css/stil.css`.
7. **Vrei să adaugi o rută nouă?** Deschide fișierul `urls.py` din aplicația respectivă.
8. **Vrei să modifici logica din spatele unei pagini?** Deschide `views.py` din aplicația respectivă.
