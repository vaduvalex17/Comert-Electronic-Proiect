# Magazin Online — Comerț Electronic (Tema II)

Aplicație web completă bazată pe arhitectura **MVC** (Model-View-Controller), construită cu **Django 5**, **SQLite** și **Bootstrap 5**. Proiectul este conceput pentru a fi ușor de rulat, înțeles și prezentat chiar și de către o persoană fără pregătire tehnică avansată.

---

## 🚀 Cum pornești aplicația (cu o singură comandă)

Aplicația include scripturi automate care configurează mediul virtual, instalează cerințele, rulează migrările și pornesc serverul local:

### Pe Linux / macOS:
```bash
chmod +x pornire.sh
./pornire.sh
```

### Pe Windows:
Dublu click pe `pornire.bat` sau rulează în terminal:
```cmd
pornire.bat
```

După pornire, deschide browserul la adresa: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 👤 Conturi demonstrative (după Faza 1)

Pentru testare și prezentare sunt create automat două conturi:
- **Administrator:** utilizator `admin` / parolă `admin123` (acces la CRUD produse și administrare)
- **Client:** utilizator `client` / parolă `client123` (cumpărături, favorite, comenzi)

---

## 📚 Ghiduri și Documentație

Toată documentația completă și explicată pe pași se află în folderul [`docs/`](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/):
- [**00-START-AICI.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/00-START-AICI.md) — Ghidul pas cu pas de pornire și depanare.
- [**01-ce-face-aplicatia.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/01-ce-face-aplicatia.md) — Prezentarea funcționalităților și corelarea cu cerințele.
- [**02-arhitectura.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/02-arhitectura.md) — Arhitectura MVC în Django și rolul fiecărui fișier.
- [**03-baza-de-date.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/03-baza-de-date.md) — Structura bazei de date și diagrama ER.
- [**04-fluxuri.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/04-fluxuri.md) — Fluxurile principale (cumpărare, administrare etc.).
- [**05-harta-codului.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/05-harta-codului.md) — „Unde găsesc funcționalitatea X în cod?”.
- [**06-glosar.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/06-glosar.md) — Dicționar de termeni tehnici explicați simplu.
- [**DECIZII.md**](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/docs/DECIZII.md) — Jurnalul deciziilor tehnice adoptate.
