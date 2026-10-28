# 05. Harta Codului Sursă

**„Vreau să găsesc X în cod, unde mă uit?”**
Tabelul de mai jos mapează fiecare funcționalitate pe fișierele și funcțiile corespunzătoare.

---

## 1. Index funcționalități

| Funcționalitate | Unde se află fișierul | Funcție / Element | Descriere scurtă |
|---|---|---|---|
| **Pornire & Configurare** | `magazin/settings.py` | Configurații generale | Setări aplicații, limbă, căi statice |
| **Cuprins URL-uri** | `magazin/urls.py` | `urlpatterns` | Direcționarea adreselor web |
| **Pagina Acasă** | `catalog/views.py` | `acasa()` | Afișare pagină principală |
| **Șablon de bază (HTML)** | `templates/baza.html` | Schelet HTML | Meniu, Bootstrap, mesaje flash, subsol |
| **Stiluri CSS proprii** | `static/css/stil.css` | Reguli CSS | Ajustări vizuale peste Bootstrap |

*(Tabelul va fi completat pe măsură ce avansăm prin fazele de dezvoltare)*

---

## 2. Ghid rapid de orientare în proiect

1. **Vrei să modifici bara de meniu sau subsolul?** Deschide [`templates/baza.html`](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/templates/baza.html).
2. **Vrei să schimbi culori sau spațieri?** Deschide [`static/css/stil.css`](file:///home/Max/Documents/Projects/Comert%20Electronic/Proiect/static/css/stil.css).
3. **Vrei să adaugi o rută nouă?** Deschide fișierul `urls.py` din aplicația respectivă.
4. **Vrei să modifici logica din spatele unei pagini?** Deschide `views.py` din aplicația respectivă.
