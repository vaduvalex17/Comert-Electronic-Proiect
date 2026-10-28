# 05. Harta Codului Sursă

**„Vreau să găsesc X în cod, unde mă uit?”**
Tabelul de mai jos mapează fiecare funcționalitate pe fișierele și funcțiile corespunzătoare.

---

## 1. Index funcționalități

| Funcționalitate | Unde se află fișierul | Funcție / Element | Descriere scurtă |
|---|---|---|---|
| **Pornire & Configurare** | `magazin/settings.py` | Configurații generale | Setări aplicații, limbă, căi statice |
| **Cuprins URL-uri** | `magazin/urls.py` | `urlpatterns` | Direcționarea adreselor web |
| **Pagina Acasă** | `catalog/views.py` | `acasa()` | Afișare pagină principală, noutăți și categorii |
| **Catalog Produse (R1.4)** | `catalog/views.py` | `lista_produse()` | Listă produse, căutare `?q=` și paginare (12/pag) |
| **Filtrare Categorie (R1.4)** | `catalog/views.py` | `produse_categorie()` | Răsfoirea produselor pe categorii |
| **Detaliu Produs (R1.3)** | `catalog/views.py` | `detaliu_produs()` | Pagina completă R1.3 (specificații, stoc, furnizor) |
| **Categorii în Navbar** | `catalog/context_processors.py` | `categorii_globale()` | Încarcă automat categoriile în meniul dropdown |
| **Șablon de bază (HTML)** | `templates/baza.html` | Schelet HTML | Meniu, Bootstrap, mesaje flash, subsol |
| **Card Produs (reutilizabil)**| `templates/partiale/card_produs.html` | Componentă HTML | Card cu poză, preț, badge stoc și link detaliu |
| **Paginare (reutilizabilă)** | `templates/partiale/paginare.html` | Componentă HTML | Navigare între pagini cu menținerea filtrelor |
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

1. **Vrei să modifici afișarea unui produs în liste?** Deschide `templates/partiale/card_produs.html`.
2. **Vrei să modifici pagina de produs individual?** Deschide `catalog/templates/catalog/detaliu_produs.html`.
3. **Vrei să modifici căutarea sau numărul de produse pe pagină?** Deschide `catalog/views.py` la funcția `lista_produse`.
4. **Vrei să modifici formularele de autentificare sau înregistrare?** Deschide `conturi/forms.py`.
5. **Vrei să vezi cum este protejată o pagină de admin?** Verifică decoratorul `@doar_admin` din `conturi/decoratori.py`.
6. **Vrei să modifici structura tabelelor sau adaugi câmpuri noi?** Deschide `catalog/models.py` sau `cumparaturi/models.py`.
