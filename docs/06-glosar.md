# 06. Glosar de Termeni Tehnici

Dicționar de noțiuni utilizate în proiect, explicate în cuvinte simple:

---

- **MVC (Model-View-Controller):** Model arhitectural de organizare a codului în trei părți: Datele (Model), Interfața vizuală (View) și Logica de coordonare (Controller).
- **ORM (Object-Relational Mapping):** Instrumentul oferit de Django prin care lucrăm cu tabelele din baza de date ca și cum ar fi obiecte normale Python, fără să scriem interogări SQL manuale.
- **Migrare (`makemigrations` / `migrate`):** Un set de instrucțiuni generate de Django pentru a sincroniza modelele din cod cu tabelele reale din fișierul `db.sqlite3`.
- **Slug:** Partea dintr-o adresă web care conține text lizibil (ex: `/categorie/laptopuri-gaming/` în loc de `/categorie/?id=4`).
- **CSRF (Cross-Site Request Forgery):** Mecanism de securitate prin care formularele HTML trimit un jeton secret (`{% csrf_token %}`) pentru a garanta că cererea vine de la utilizatorul legitim al site-ului.
- **Tranzacție atomică (`transaction.atomic`):** O operațiune de tip „totul sau nimic”: dacă la plasarea comenzii scade stocul dar plata eșuează, toate modificările din baza de date sunt anulate automat pentru a nu lăsa date corupte.
- **Soft-delete:** O tehnică prin care o înregistrare nu este ștearsă definitiv de pe disc, ci este doar marcată ca inactivă (`activ=False`), pentru a păstra integritatea istoricului comenzilor.
- **FBV (Function-Based View):** O funcție Python simplă care primește o cerere de la browser (`request`) și returnează un răspuns (de obicei o pagină HTML compilată).
- **Algoritmul Luhn (Mod 10):** Formula matematică de control utilizată la nivel global pentru validarea structurală a numerelor de carduri bancare (Visa, Mastercard etc.).
- **IDOR (Insecure Direct Object Reference):** Vulnerabilitate de securitate în care un utilizator ar putea accesa resursele altui utilizator prin simpla modificare a ID-ului din URL. În proiect, comanda este protejată strict prin `utilizator=request.user`, returnând `404 Not Found`.
- **Cumpărător Verificat (Verified Purchase):** Sistem de recenzii în care doar utilizatorii care au comandat și achiziționat produsul au permisiunea de a acorda o notă (1-5 stele) și a lăsa un comentariu.
- **Context Processor:** Funcție Django care injectează automat variabile globale (ex: numărul de produse din coș, numărul de favorite) în contextul fiecărui șablon HTML randat pe site.
