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

## 👤 Conturi demonstrative (Gata create)

Pentru testare și prezentare sunt create automat două conturi:
- **Administrator:** utilizator `admin` / parolă `admin123` (acces la CRUD produse, gestiune comenzi, dashboard statistici)
- **Client:** utilizator `client` / parolă `client123` (cumpărături, favorite, checkout card Luhn, istoric comenzi, recenzii)

### 🏷️ Coduri Promoționale Demo (Cupoane):
- `GAMING10`: 10% reducere fără limită minimă
- `ELECTRO20`: 20% reducere pentru comenzi de minimum 1000 lei
- `STUDENT15`: 15% reducere pentru comenzi de minimum 200 lei

---

## 🧪 Teste Automate

Proiectul conține o suită extinsă de **73 de teste automate** care verifică integritatea modelelor, securitatea IDOR (404), algoritmul Luhn, tranzacția atomică ACID la finalizare și operatorii logici ȘI/SAU:

```bash
./venv/bin/python manage.py test        # Linux / macOS
venv\Scripts\python manage.py test       # Windows
```

---

## 📚 Ghiduri și Documentație

Toată documentația completă și explicată pe pași se află în folderul [`docs/`](docs/):
- [**00-START-AICI.md**](docs/00-START-AICI.md) — Ghidul pas cu pas de pornire și depanare.
- [**01-ce-face-aplicatia.md**](docs/01-ce-face-aplicatia.md) — Prezentarea funcționalităților și corelarea cu cerințele.
- [**02-arhitectura.md**](docs/02-arhitectura.md) — Arhitectura MVC în Django și rolul fiecărui fișier.
- [**03-baza-de-date.md**](docs/03-baza-de-date.md) — Structura bazei de date și diagrama ER.
- [**04-fluxuri.md**](docs/04-fluxuri.md) — Fluxurile principale (cumpărare, administrare etc.).
- [**05-harta-codului.md**](docs/05-harta-codului.md) — „Unde găsesc funcționalitatea X în cod?”.
- [**06-glosar.md**](docs/06-glosar.md) — Dicționar de termeni tehnici explicați simplu.
- [**DECIZII.md**](docs/DECIZII.md) — Jurnalul deciziilor tehnice adoptate.

## 🎤 Slide-uri pentru raportări

În folderul [`prezentare/`](prezentare/) se află slide-urile gata făcute (PowerPoint, editabile):
- `Raportarea-I.pptx` — săptămâna 7/8 (R1.1–R1.4)
- `Raportarea-II.pptx` — săptămâna 11/12 (R2.1–R2.3 + bonusuri)

Fiecare slide are în **notele vorbitorului** (Notes, sub slide) textul de spus la prezentare.
Înainte de prezentare, înlocuiește `[Numele tău]` de pe primul slide.
