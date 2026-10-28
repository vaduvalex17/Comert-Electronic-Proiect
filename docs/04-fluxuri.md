# 04. Fluxurile Aplicației

Acest document arată, pas cu pas, ce se întâmplă „în spatele ecranului” la cele mai importante acțiuni.
Diagramele se citesc de sus în jos: fiecare săgeată este un mesaj de la cineva către altcineva.

---

## 1. Autentificarea (Login) — R1.1

```mermaid
sequenceDiagram
    actor U as Utilizator
    participant B as Browser
    participant V as conturi/views.py<br/>login_utilizator()
    participant DB as Baza de date

    U->>B: Completează utilizator + parolă, apasă „Conectare”
    B->>V: Cerere POST (cu token CSRF)
    V->>DB: Caută utilizatorul și compară hash-ul parolei
    alt Date corecte
        V->>DB: Creează o sesiune nouă
        V-->>B: Cookie „sessionid” + redirecționare (Acasă sau pagina din ?next=, doar dacă e din site)
        B-->>U: Meniul arată numele și, pentru admin, secțiunea Administrare
    else Date greșite
        V-->>B: Formularul din nou, cu mesaj de eroare
    end
```

**De reținut:** parola nu este salvată niciodată „în clar”, ci doar sub formă de *hash* (o amprentă din care parola nu poate fi refăcută).
La login, Django calculează hash-ul parolei introduse și îl compară cu cel salvat.

---

## 2. Adăugarea unui produs de către admin — R1.2

```mermaid
sequenceDiagram
    actor A as Admin
    participant D as @doar_admin<br/>(conturi/decoratori.py)
    participant V as catalog/views_admin.py<br/>admin_produs_adauga()
    participant F as ProdusForm<br/>(catalog/forms.py)
    participant DB as Baza de date

    A->>D: Deschide /administrare/produse/adauga/
    D->>D: E logat? Are is_staff=True?
    alt Nu este admin
        D-->>A: Redirecționare (login sau Acasă) cu mesaj „Acces refuzat”
    else Este admin
        D->>V: Permite accesul
        V-->>A: Formular gol
        A->>V: Trimite formularul completat (POST, cu poză opțională)
        V->>F: Validează: preț > 0, stoc ≥ 0, minimum o livrare
        alt Date valide
            F->>DB: Salvează produsul (slug generat automat din nume)
            V-->>A: Mesaj de succes + tabelul de produse
        else Erori
            V-->>A: Formularul cu câmpurile greșite marcate cu roșu
        end
    end
```

**Ștergerea** urmează aceeași cale, cu o regulă în plus:
- dacă produsul **nu** a fost comandat niciodată, este șters fizic din baza de date;
- dacă produsul **a fost** comandat, este doar dezactivat (`activ=False`, *soft-delete*): dispare din catalog, dar comenzile vechi rămân complete.

---

## 3. Fluxul de cumpărare (Checkout) — R2.2

```mermaid
sequenceDiagram
    actor C as Client
    participant P as Pagina produs
    participant Cos as Coș
    participant F as Finalizare comandă
    participant S as servicii.plaseaza_comanda()
    participant DB as Baza de date

    C->>P: Apasă „Adaugă în coș”
    P->>DB: Salvează produsul în ArticolCos (cantitatea nu poate depăși stocul)
    C->>Cos: Vede produsele, modifică cantități, aplică un cupon
    Cos-->>C: Subtotal − reducere + cost livrare = Total (doar livrările comune tuturor produselor)
    C->>F: Completează adresa, livrarea și cardul
    F->>F: Validează cardul: algoritm Luhn, expirare în viitor, CVV de 3 cifre
    F->>S: Datele sunt valide
    Note over S,DB: Tranzacție atomică: totul sau nimic
    S->>DB: Blochează produsele și verifică stocul
    S->>DB: Scade stocul
    S->>DB: Creează Comanda + ArticolComanda (copie a prețului de acum)
    S->>DB: Golește coșul
    S-->>C: Pagina de confirmare (cardul apare ca **** 4242)
```

Dacă între timp stocul nu mai ajunge (de exemplu, alt client a cumpărat ultima bucată), tranzacția este anulată:
nu se salvează nicio comandă, stocul rămâne neatins, iar clientul primește un mesaj care numește produsul.

---

## 4. Istoricul comenzilor — R2.3

```mermaid
sequenceDiagram
    actor C as Client
    participant V as cumparaturi/views.py
    participant DB as Baza de date

    C->>V: Deschide „Comenzile mele” (/comenzi/)
    V->>DB: Comenzile WHERE utilizator = clientul logat
    V-->>C: Tabel cu data, numărul, totalul și statusul fiecărei comenzi
    C->>V: Apasă „Detalii” (/comenzi/7/)
    V->>DB: Comanda 7 WHERE utilizator = clientul logat
    alt Comanda îi aparține
        V-->>C: Detaliul comenzii (produse, adresă, livrare, card mascat)
    else Este comanda altcuiva sau nu există
        V-->>C: Eroare 404 „Pagina nu există”
    end
```

**De ce 404 și nu „Acces interzis”?** Un mesaj de tip „nu ai voie” ar confirma că acea comandă există.
Cu 404, un client curios nu află nimic despre comenzile altora.
