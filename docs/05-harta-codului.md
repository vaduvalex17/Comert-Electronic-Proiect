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
| **Formular Produs (R1.2)** | `catalog/forms.py` | `ProdusForm` | ModelForm cu validări de preț, stoc și livrare |
| **Listă Admin Produse (R1.2)**| `catalog/views_admin.py` | `admin_produse_lista()` | Tabel admin cu filtre, stări activ/inactiv |
| **Adăugare Produs (R1.2)** | `catalog/views_admin.py` | `admin_produs_adauga()` | Formular adăugare produs nou de către admin |
| **Editare Produs (R1.2)** | `catalog/views_admin.py` | `admin_produs_editeaza()` | Actualizare preț, stoc, imagine etc. |
| **Ștergere / Soft-Delete (R1.2)**| `catalog/views_admin.py` | `admin_produs_sterge()` | Ștergere fizică sau dezactivare dacă are comenzi |
| **Lista Favorite / Wishlist (R2.1)**| `cumparaturi/views.py` | `lista_favorite()` | Vizualizare produse salvate de client |
| **Toggle Favorit (POST) (R2.1)**| `cumparaturi/views.py` | `adauga_elimina_favorit()`| Adăugare/eliminare cu inimă pe card sau detaliu |
| **Mută în coș (R2.1)** | `cumparaturi/views.py` | `muta_in_cos()` | Mutare produs din favorite în coșul activ |
| **Contoare Coș & Favorite** | `cumparaturi/context_processors.py` | `cumparaturi_meniu()` | Calculează insignele numerice din meniul de sus |
| **Categorii în Navbar** | `catalog/context_processors.py` | `categorii_globale()` | Încarcă automat categoriile în meniul dropdown |
| **Șablon de bază (HTML)** | `templates/baza.html` | Schelet HTML | Meniu, Bootstrap, mesaje flash, subsol |
| **Card Produs (reutilizabil)**| `templates/partiale/card_produs.html` | Componentă HTML | Card cu poză, preț, inimă favorit, badge stoc |
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

1. **Vrei să modifici lista de favorite (Wishlist)?** Deschide `cumparaturi/templates/cumparaturi/favorite.html` și `cumparaturi/views.py`.
2. **Vrei să modifici butonul de inimă?** Deschide `templates/partiale/card_produs.html` sau `catalog/templates/catalog/detaliu_produs.html`.
3. **Vrei să modifici panoul de administrare produse?** Deschide `catalog/views_admin.py` și `catalog/templates/catalog/admin/`.
4. **Vrei să modifici căutarea sau paginarea?** Deschide `catalog/views.py`.
5. **Vrei să modifici formularele de conturi?** Deschide `conturi/forms.py`.
