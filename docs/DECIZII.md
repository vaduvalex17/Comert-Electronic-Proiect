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
