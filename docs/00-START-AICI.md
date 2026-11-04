# Ghid de pornire rapidă: 00-START-AICI

Acest ghid este dedicat utilizatorului non-tehnic. Urmează pașii de mai jos pentru a porni și testa magazinul online pe calculatorul tău.

---

## Pasul 1: Verifică dacă ai Python instalat

Aplicația necesită **Python 3.12** sau o versiune mai nouă (funcționează și cu 3.10 / 3.11, dar 3.12+ e recomandat).
Deschide un terminal (pe Linux/macOS) sau Command Prompt / PowerShell (pe Windows) și tastează:

```bash
python3 --version
```
*(pe Windows poți tasta și simplu `python --version`)*

Dacă apare o versiune de forma `Python 3.12.x` sau `Python 3.14.x`, totul este în regulă.

> **Pe Windows nu trebuie să verifici nimic:** dacă Python lipsește, `pornire.bat` îl instalează singur (prin `winget`, are nevoie de internet). Dacă Windows întreabă „Permiteți acestei aplicații să facă modificări?”, apasă **Da**. Dacă la final fereastra îți cere să pornești din nou, închide-o și dă iar dublu click pe `pornire.bat`.
>
> Doar dacă instalarea automată nu e posibilă, se deschide pagina [python.org](https://www.python.org/downloads/): instalează Python și **bifează neapărat căsuța „Add python.exe to PATH”**.

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
0. Pe Windows: găsește Python sau, dacă lipsește, îl instalează automat.
1. Verifică dacă există mediul virtual Python (`venv`). Dacă nu, îl creează automat.
2. Instalează dependențele necesare (`Django` și `Pillow`).
3. Creează tabelele în baza de date locală SQLite (`migrate`).
4. Încarcă datele demonstrative (produse, categorii, conturi de test).
5. Pornește serverul web local la adresa `http://127.0.0.1:8000` (dacă portul 8000 e ocupat, alege singur 8001, 8002 ...).
6. Pe Windows: deschide singur browserul pe pagina magazinului, când acesta e gata.

---

## Pasul 3: Accesarea aplicației în browser

Pe Windows, browserul se deschide singur după câteva secunde. Dacă nu se deschide (sau ești pe Linux/macOS), deschide orice browser web (Chrome, Firefox, Edge, Safari) și navighează la adresa afișată în fereastră, de obicei:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Pasul 4: Oprirea serverului

Când ai terminat prezentarea sau testarea:
- În terminalul în care rulează aplicația, apasă tastele **Ctrl + C**. Serverul se va opri în siguranță.

---

## Probleme frecvente și soluții rapide

| Problemă | Cauză probabilă | Soluție |
|---|---|---|
| Fereastra scrie „Portul 8000 este ocupat” | Serverul a rămas pornit într-o altă fereastră | Nu e o problemă: scriptul alege singur portul următor. Ca să eviți confuzia, închide fereastra veche |
| `No module named django` | Nu este activat mediul virtual | Folosește direct scriptul `./pornire.sh` sau `pornire.bat` |
| Fereastra scrie „Python s-a instalat. Inchide aceasta fereastra...” | Python tocmai a fost instalat automat | Închide fereastra și dă din nou dublu click pe `pornire.bat` |
| Se deschide pagina python.org | Instalarea automată nu e disponibilă pe acel Windows | Instalează Python, bifează „Add python.exe to PATH”, apoi dă din nou dublu click pe `pornire.bat` |
| `'python3' / 'python' is not recognized` | La fel ca mai sus | La fel ca mai sus |
| Pe Windows apare „Windows protected your PC” la dublu click | Filtrul SmartScreen | Apasă „More info” → „Run anyway” (scriptul e doar text și poate fi citit cu Notepad) |
| Pagina nu se încarcă în browser | Serverul nu rulează | Fereastra neagră a scriptului trebuie să rămână deschisă cât timp folosești site-ul |
| Vreau să o iau de la zero cu datele demo | — | Oprește serverul, șterge fișierul `db.sqlite3` și pornește din nou scriptul |
| Imaginile produselor nu se văd | Lipsește folderul `media/` | Folderul se generează automat la încărcarea primului produs |
