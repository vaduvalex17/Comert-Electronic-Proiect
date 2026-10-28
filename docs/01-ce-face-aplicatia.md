# 01. Ce face aplicația

Aplicația este un magazin electronic complet care permite vânzarea de produse online, acoperind toate fluxurile standard de e-commerce.

---

## 1. Rolurile utilizatorilor

În magazin există două roluri distincte:
1. **Vizitator / Client:**
   - Poate explora catalogul de produse și categoriile.
   - Poate căuta produse după nume sau descriere.
   - Își poate crea un cont propriu și se poate autentifica.
   - Poate adăuga produse în lista de favorite (Wishlist).
   - Poate adăuga produse în coșul de cumpărături și poate modifica cantitățile.
   - Poate finaliza o comandă (introducând datele de livrare și datele simulate de card).
   - Poate consulta istoricul propriilor comenzi plasate.

2. **Administrator (Admin / Staff):**
   - Are acces la panoul de administrare a catalogului.
   - Poate adăuga produse noi cu toate specificațiile cerute.
   - Poate edita datele produselor existente (preț, stoc, imagine etc.).
   - Poate șterge produse (cu protecție: dacă un produs a fost deja comandat în trecut, acesta devine inactiv pentru a nu distruge istoricul comenzilor).
   - Are acces și la panoul nativ Django (`/admin/`).

---

## 2. Corelarea cu cerințele oficiale de notare

### Raportarea I (Săptămâna 7/8 — 40% din nota de proiect)
- **R1.1 Autentificare:** Login și înregistrare diferențiate (client vs. admin).
- **R1.2 Gestiune produse:** Adăugare, editare și ștergere de produse din interfață.
- **R1.3 Câmpurile unui produs:** Nume, descriere, specificații detaliate, preț, stoc, furnizor, modalități de livrare, categorie.
- **R1.4 Răsfoire catalog:** Navigare pe categorii, căutare produse, paginare.

### Raportarea II (Săptămâna 11/12 — 60% din nota de proiect)
- **R2.1 Wishlist / Favorite:** Salvarea produselor preferate și posibilitatea mutării lor în coș.
- **R2.2 Flow de cumpărare:** Coș interactiv, alegere modalitate livrare, calcul automat total, formular de livrare și date card (simulat).
- **R2.3 Istoric comenzi:** Vizualizarea comenzilor anterioare cu detalii complete și status.
