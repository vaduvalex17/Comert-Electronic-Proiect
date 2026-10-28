"""
catalog/views.py

Controllere (views) pentru răsfoirea catalogului de produse:
- Pagina principală (acasă)
- Lista produselor și căutare
- Detaliu produs
- Produse filtrate după categorie
"""

from django.shortcuts import render


def acasa(request):
    """Afișează pagina principală a magazinului.

    În Faza 0 oferă o pagină introductivă de bun venit care confirmă
    că scheletul aplicației funcționează corect.
    """
    # Pasul 1: Pregătim contextul transmis către template
    context = {
        'titlu': 'Bun venit la Magazinul Online',
        'mesaj_bun_venit': 'Proiect Comerț Electronic — Aplicație Web MVC realizată cu Django și Bootstrap 5.',
    }

    # Pasul 2: Răspundem cu template-ul paginii principale
    return render(request, 'catalog/acasa.html', context)
