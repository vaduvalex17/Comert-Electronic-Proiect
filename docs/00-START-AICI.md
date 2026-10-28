# Ghid de pornire rapidă: 00-START-AICI

Acest ghid este dedicat utilizatorului non-tehnic. Urmează pașii de mai jos pentru a porni și testa magazinul online pe calculatorul tău.

---

## Pasul 1: Verifică dacă ai Python instalat

Aplicația necesită **Python 3.12** sau o versiune mai nouă.
Deschide un terminal (pe Linux/macOS) sau Command Prompt / PowerShell (pe Windows) și tastează:

```bash
python3 --version
```
*(pe Windows poți tasta și simplu `python --version`)*

Dacă apare o versiune de forma `Python 3.12.x` sau `Python 3.14.x`, totul este în regulă. Dacă comanda nu este recunoscută, descarcă și instalează Python de pe [python.org](https://www.python.org/downloads/). La instalare pe Windows, **bifează neapărat căsuța „Add python.exe to PATH”**.

---

## Pasul 2: Pornirea aplicației dintr-o singură comandă

În folderul proiectului găsești un script automat:

- **Pe Linux / macOS:**
  ```bash
  ./pornire.sh
  ```
  *(Dacă primești mesaj de permisiune refuzată, rulează o singură dată `chmod +x pornire.sh`)*

- **Pe Windows:**
  Fă dublu click pe fișierul `pornire.bat` sau deschide terminalul în acest folder și tastează:
  ```cmd
  pornire.bat
  ```

### Ce face acest script în fundal?
1. Verifică dacă există mediul virtual Python (`venv`). Dacă nu, îl creează automat.
2. Instalează dependențele necesare (`Django` și `Pillow`).
3. Creează tabelele în baza de date locală SQLite (`migrate`).
4. Încarcă datele demonstrative (produse, categorii, conturi de test).
5. Pornește serverul web local la adresa `http://127.0.0.1:8000`.

---

## Pasul 3: Accesarea aplicației în browser

Deschide orice browser web (Chrome, Firefox, Edge, Safari) și navighează la:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Pasul 4: Oprirea serverului

Când ai terminat prezentarea sau testarea:
- În terminalul în care rulează aplicația, apasă tastele **Ctrl + C**. Serverul se va opri în siguranță.

---

## Probleme frecvente și soluții rapide

| Problemă | Cauză probabilă | Soluție |
|---|---|---|
| `Port 8000 already in use` | Serverul a rămas pornit într-o altă fereastră | Oprește procesul precedent sau rulează `python manage.py runserver 8080` |
| `No module named django` | Nu este activat mediul virtual | Folosește direct scriptul `./pornire.sh` sau `pornire.bat` |
| Imaginile produselor nu se văd | Lipsește folderul `media/` | Folderul se generează automat la încărcarea primului produs |
