# 06. Glosar de Termeni Tehnici

Dicționar de noțiuni folosite în proiect, explicate în cuvinte simple. Termenii sunt grupați pe teme.

---

## 1. Cum funcționează un site web

- **Browser:** Programul cu care vizitezi site-uri (Chrome, Firefox, Edge). El trimite *cereri* și afișează *răspunsurile*.
- **Server:** Programul care primește cererile și răspunde cu pagini. La noi, serverul pornește cu `python manage.py runserver` și rulează pe calculatorul tău, la adresa `http://127.0.0.1:8000` (`127.0.0.1` înseamnă „acest calculator”).
- **URL (adresă web):** Textul din bara de adrese, de exemplu `/produse/` sau `/produs/laptop-dell-xps-15-9530/`. Fișierele `urls.py` decid ce funcție răspunde la fiecare adresă.
- **Cerere GET:** O cerere care doar *citește* ceva, de exemplu deschiderea unei pagini. Nu modifică date.
- **Cerere POST:** O cerere care *trimite* date ca să schimbe ceva: un formular, adăugarea în coș, ștergerea unui produs. În proiect, orice acțiune care modifică date se face obligatoriu prin POST.
- **Redirecționare (redirect):** Răspunsul „du-te la altă adresă”. De exemplu, după ce adaugi un produs în coș, ești trimis la pagina coșului.
- **Cod 404:** Răspunsul „pagina nu există”. Îl folosim și ca să ascundem comenzile altor clienți.
- **Cookie:** O mică bucată de text pe care site-ul o salvează în browser și pe care browserul o trimite înapoi la fiecare cerere.
- **Sesiune:** Felul în care site-ul „ține minte” cine ești între două pagini. După login, browserul primește un cookie cu un cod aleator, iar serverul știe ce utilizator corespunde codului. Tot în sesiune păstrăm cuponul aplicat și livrarea aleasă.

## 2. Arhitectura (cum e organizat codul)

- **MVC (Model-View-Controller):** Mod de organizare a codului în trei părți: datele (Model), ce vede utilizatorul (View) și logica care le leagă (Controller).
- **Django:** Framework-ul (o „trusă de construcție”) scris în Python pe care e făcut proiectul. Vine gata cu login, formulare, bază de date și securitate de bază.
- **Framework:** Un schelet gata făcut pentru un tip de aplicații. Programatorul scrie doar părțile specifice proiectului.
- **Model:** O clasă Python care descrie un tabel din baza de date (de ex. `Produs`, cu câmpurile nume, preț, stoc...). Se află în `models.py`.
- **View (în Django):** O funcție Python care primește o cerere și întoarce o pagină. Joacă rolul de *Controller* din MVC. Se află în `views.py`.
- **Template (șablon):** Un fișier `.html` cu „găuri” (`{{ produs.nume }}`) pe care Django le completează cu date. Joacă rolul de *View* din MVC.
- **FBV (Function-Based View):** View scris ca o funcție simplă: o funcție = o pagină. L-am preferat variantei cu clase pentru claritate.
- **Aplicație Django:** Un folder cu o parte bine delimitată a proiectului. Avem trei: `conturi`, `catalog` și `cumparaturi`.
- **Context processor:** O funcție care adaugă automat date pe *toate* paginile, de exemplu numărul de produse din coș afișat în meniu.
- **Decorator:** O „etichetă” pusă deasupra unei funcții (`@login_required`, `@doar_admin`) care adaugă o verificare înainte ca funcția să ruleze. De exemplu, „doar adminii pot intra aici”.
- **Formular (Form / ModelForm):** O clasă care descrie câmpurile unui formular HTML și regulile de validare (ex: prețul trebuie să fie pozitiv). `ModelForm` construiește formularul automat dintr-un model.
- **Bootstrap:** O bibliotecă de stiluri CSS gata făcute (butoane, tabele, meniuri) care dă aplicației un aspect modern fără mult cod propriu.
- **Static / Media:** *Static* sunt fișierele fixe ale site-ului (CSS, logo, ilustrații). *Media* sunt fișierele încărcate de utilizatori (pozele produselor).

## 3. Baza de date

- **Bază de date:** Locul unde se păstrează toate informațiile magazinului. Folosim **SQLite**, adică un singur fișier, `db.sqlite3`.
- **Tabel / înregistrare / câmp:** Un tabel seamănă cu o foaie Excel. Fiecare rând este o *înregistrare* (un produs), iar fiecare coloană un *câmp* (preț, stoc).
- **Cheie primară (id):** Numărul unic al fiecărui rând (produsul 1, produsul 2...).
- **ForeignKey (FK, cheie străină):** O legătură „mai mulți la unul”. Fiecare produs are *o* categorie, dar o categorie are *mai multe* produse.
- **ManyToMany (M2M):** O legătură „mai mulți la mai mulți”. Un produs poate avea mai multe metode de livrare, iar o metodă de livrare servește mai multe produse.
- **ORM (Object-Relational Mapping):** Unealta din Django prin care lucrăm cu baza de date prin cod Python (`Produs.objects.filter(activ=True)`), fără să scriem SQL de mână.
- **SQL / SQL Injection:** SQL este limbajul bazelor de date. *SQL Injection* este un atac în care cineva introduce cod SQL într-un formular. ORM-ul ne protejează automat.
- **Migrare (`makemigrations` / `migrate`):** Instrucțiuni generate de Django care aduc tabelele din `db.sqlite3` la zi cu modelele din cod.
- **Slug:** Varianta „prietenoasă” a unui nume, folosită în adrese: `laptop-dell-xps-15-9530` în loc de `?id=17`.
- **Tranzacție atomică (`transaction.atomic`):** O operațiune „totul sau nimic”. Dacă la plasarea comenzii un pas eșuează, toate modificările de până atunci sunt anulate.
- **Snapshot:** O copie „înghețată” a unei valori la un moment dat. În comandă copiem numele și prețul produsului, ca o scumpire ulterioară să nu schimbe comenzile vechi.
- **Soft-delete:** În loc să ștergem un rând, îl marcăm ca inactiv (`activ=False`), ca istoricul comenzilor să rămână complet.
- **Decimal:** Tipul de număr folosit pentru bani. Spre deosebire de `float`, nu produce erori de rotunjire (`0.1 + 0.2` dă exact `0.3`).
- **Comandă de management (`populeaza_date`):** Un script rulat cu `python manage.py ...`. Al nostru umple baza de date cu produse și conturi demo.

## 4. Securitate

- **Autentificare / autorizare:** *Autentificarea* verifică cine ești (login). *Autorizarea* verifică ce ai voie să faci (admin sau client).
- **Hash parolă:** Parolele nu se salvează ca text, ci ca *hash*: o amprentă calculată cu un algoritm (PBKDF2-SHA256) din care parola nu poate fi refăcută.
- **CSRF (Cross-Site Request Forgery):** Atac prin care alt site încearcă să trimită formulare în numele tău. Fiecare formular al nostru conține un cod secret (`{% csrf_token %}`) pe care un site străin nu îl poate ghici.
- **IDOR (Insecure Direct Object Reference):** Vulnerabilitatea în care schimbi un număr din adresă și vezi datele altcuiva. La noi, comenzile se caută mereu împreună cu `utilizator=request.user`, iar comanda altcuiva dă 404.
- **Open redirect:** Vulnerabilitatea în care un site te trimite, după login, pe o adresă externă aleasă de un atacator. Funcția `redirectioneaza_sigur()` acceptă doar adrese din propriul site.
- **Algoritmul Luhn (Mod 10):** Formula de control cu care se verifică dacă un număr de card are o structură validă (prinde greșelile de tastare).
- **PCI-DSS:** Standardul de securitate pentru datele de card. Regula de bază pe care o respectăm: nu salvăm niciodată numărul complet al cardului și nici CVV-ul.
- **Cumpărător verificat:** Doar clienții care au comandat produsul pot lăsa o recenzie.

## 5. Unelte de dezvoltare

- **Python:** Limbajul de programare în care e scris proiectul.
- **Mediu virtual (`venv`):** Un folder cu o copie separată de Python și pachetele proiectului, ca să nu se amestece cu alte programe de pe calculator.
- **pip / `requirements.txt`:** *pip* instalează pachete Python. `requirements.txt` este lista pachetelor necesare (Django și Pillow).
- **Pillow:** Biblioteca Python care lucrează cu imagini (folosită la poza produselor).
- **Teste automate:** Cod care verifică automat că aplicația se comportă corect (`python manage.py test`). Proiectul are 73.
- **Git / commit:** *Git* păstrează istoricul tuturor modificărilor. Un *commit* este un „punct de salvare” cu o descriere.
- **Mermaid:** Limbajul în care sunt desenate diagramele din documentație. GitHub și VS Code le afișează automat.
