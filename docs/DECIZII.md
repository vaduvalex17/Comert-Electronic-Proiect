# Jurnalul Deciziilor Tehnice (Architecture Decision Records)

Toate deciziile de arhitectură, convențiile alese și eventualele abateri justificate de la planul inițial sunt consemnate în acest document.

---

## Decizia 01: Folosirea exclusivă a Function-Based Views (FBV)
- **Data:** Octombrie 2026
- **Context:** În Django se pot folosi fie Class-Based Views (CBV), fie Function-Based Views (FBV).
- **Decizie:** Am optat exclusiv pentru FBV.
- **Motivație:** Proiectul este susținut de un student fără experiență tehnică profundă. Într-o funcție Python, pașii sunt vizibili în ordine secvențială (primire cerere -> validare -> salvare -> render), fără moștenire magică de clase greu de explicat la evaluare.

---

## Decizia 02: Baza de date SQLite
- **Data:** Octombrie 2026
- **Context:** Alegerea motorului de baze de date (PostgreSQL / MySQL vs SQLite).
- **Decizie:** SQLite salvat în `db.sqlite3`.
- **Motivație:** Nu necesită instalarea sau configurarea vreunui serviciu suplimentar (server de baze de date, porturi, utilizatori, permisiuni), funcționând instantaneu „out of the box” pe orice calculator.

---

## Decizia 03: Bootstrap 5 prin CDN
- **Data:** Octombrie 2026
- **Context:** Interfața grafică și stilizarea paginilor.
- **Decizie:** Folosirea Bootstrap 5.3 și Bootstrap Icons direct prin CDN, fără Node.js sau pas de build.
- **Motivație:** Simplifică la maximum distribuirea și rularea proiectului. Colegul nu trebuie să aibă npm/Node instalate.

---

## Decizia 04: Coșul de cumpărături salvat în baza de date
- **Data:** Octombrie 2026
- **Context:** Un coș poate fi ținut în sesiune (temporar, în browser) sau în baza de date (tabelul `ArticolCos`).
- **Decizie:** Baza de date.
- **Motivație:** Coșul se păstrează între autentificări și pe alt calculator. E și mai ușor de explicat: e încă un tabel, ca toate celelalte. Prețul: coșul există doar pentru utilizatorii logați.

---

## Decizia 05: Specificațiile produsului ca text „Cheie: Valoare”
- **Data:** Octombrie 2026
- **Context:** Specificațiile puteau fi un tabel separat, cu rânduri adăugate dinamic în formular.
- **Decizie:** Un singur câmp text, câte o specificație pe linie (`Procesor: Intel i5`), transformat în tabel de metoda `Produs.specificatii_lista()`.
- **Motivație:** Formularul rămâne simplu, iar adminul poate scrie oricâte specificații. Dezavantaj acceptat: specificațiile nu pot fi filtrate individual.

---

## Decizia 06: Soft-delete pentru produsele deja comandate
- **Data:** Octombrie 2026
- **Context:** Ștergerea unui produs care apare în comenzi ar lăsa comenzile vechi fără referință.
- **Decizie:** Produsele fără comenzi se șterg fizic. Cele comandate se marchează `activ=False`.
- **Motivație:** Istoricul clienților rămâne complet. În plus, comanda păstrează oricum o copie a numelui și a prețului (`ArticolComanda`).

---

## Decizia 07: Prețuri copiate în comandă (snapshot)
- **Data:** Octombrie 2026
- **Decizie:** `Comanda` și `ArticolComanda` salvează subtotalul, costul livrării, reducerea, totalul, plus numele și prețul unitar al fiecărui produs.
- **Motivație:** Dacă adminul schimbă ulterior un preț sau costul unei livrări, comenzile trecute rămân neschimbate, ca o factură reală.

---

## Decizia 08: Plată simulată, fără stocarea datelor de card
- **Data:** Octombrie 2026
- **Decizie:** Formularul validează cardul (Luhn, expirare, CVV), dar nu procesează nicio plată. Se salvează doar ultimele 4 cifre.
- **Motivație:** Cerința cere „introducere date card”, nu o integrare cu un procesator de plăți. Păstrarea numărului complet sau a CVV-ului ar încălca regulile PCI-DSS.

---

## Decizia 09: Redirecționări sigure (protecție „open redirect”)
- **Data:** Octombrie 2026 (corecție după verificarea finală)
- **Context:** După login (`?next=`) și după acțiuni din catalog (header-ul `Referer`), aplicația trimite utilizatorul înapoi pe pagina anterioară. Adresa vine din browser și poate fi falsificată.
- **Decizie:** Toate aceste redirecționări trec prin `conturi/redirectionari.py: redirectioneaza_sigur()`, care acceptă doar adrese din propriul site.
- **Motivație:** Previne trimiterea utilizatorului pe un site de phishing după login.

---

## Decizia 10: Ilustrații implicite pe categorii și livrări diferite în datele demo
- **Data:** Octombrie 2026 (corecție după verificarea finală)
- **Decizie:**
  - Produsele fără poză afișează o ilustrație a categoriei lor (`static/img/categorii/`, proprietatea `Produs.imagine_implicita`).
  - În datele demo, laptopul ASUS ROG, soundbar-ul Samsung și monitorul LG nu au livrare prin Easybox.
- **Motivație:** Catalogul arată mai bine fără să folosim fotografii protejate de drepturi de autor. Intersecția livrărilor din coș se poate demonstra concret la prezentare.

---

## Decizia 11: `pornire.bat` instalează Python și deschide singur browserul
- **Data:** Noiembrie 2026
- **Context:** Colegul care prezintă nu are experiență tehnică. Pașii manuali (instalarea Python cu „Add python.exe to PATH”, scrierea adresei în browser) erau cele mai probabile surse de blocaj.
- **Decizie:** Pe Windows, scriptul caută Python 3.10+ (`py`, `python`, folderul implicit de instalare) și, dacă lipsește, îl instalează cu `winget` doar pentru utilizatorul curent. Alege primul port liber începând cu 8000 și deschide browserul când serverul răspunde.
- **Motivație:** Pornirea devine un singur dublu click. Aplicația în sine nu se schimbă: modificarea privește doar scriptul de pornire.
