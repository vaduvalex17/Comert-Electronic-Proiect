# 04. Fluxurile Aplicației

Acest document descrie modul în care circulă datele în timpul celor mai importante acțiuni ale utilizatorului.

---

## 1. Fluxul de Cumpărare (Checkout)

```mermaid
sequenceDiagram
    actor C as Client
    participant P as Pagina Produs
    participant Cos as Cos Cumparaturi
    participant F as Formular Finalizare
    participant S as Serviciu Comanda
    participant DB as Baza de Date

    C->>P: Apasa "Adauga in cos"
    P->>DB: Salveaza produsul in ArticolCos
    C->>Cos: Vizualizeaza produsele si alege livrarea
    Cos-->>C: Calculeaza Subtotal + Livrare = Total
    C->>F: Completeaza adresa si datele de card
    F->>S: Trimite formularul validat
    Note over S,DB: Tranzactie Atomica (totul sau nimic)
    S->>DB: Verifica stocul disponibil
    S->>DB: Scade stocul produselor
    S->>DB: Creeaza Comanda si Articolele de comanda (snapshot)
    S->>DB: Goleste cosul de cumparaturi
    S-->>C: Redirectioneaza catre pagina de confirmare a comenzii
```

---

## 2. Fluxul de Administrare a Produselor (Admin)

1. Administratorul se autentifică cu contul de staff.
2. Accesează panoul `/administrare/produse/`.
3. Completează formularul de adăugare/editare produs (inclusiv imagine și modalități de livrare).
4. La salvare, Django validează câmpurile (preț pozitiv, stoc nenegativ, slug unic).
5. La ștergere:
   - Dacă produsul **nu** a fost comandat niciodată: este șters fizic din baza de date.
   - Dacă produsul **a fost** inclus în comenzi: este dezactivat (`activ=False`), ascuns din catalogul public, dar păstrat pentru evidența comenzilor anterioare.
