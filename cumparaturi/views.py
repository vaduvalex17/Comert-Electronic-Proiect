"""
cumparaturi/views.py

Controllere (views) pentru gestionarea listei de produse favorite (Wishlist - Cerința R2.1):
- lista_favorite: afișează produsele salvate de utilizator
- adauga_elimina_favorit: comută starea de favorit (adaugă sau scoate produsul) prin POST
- elimina_favorit: elimină un articol direct din pagina de favorite prin POST
- muta_in_cos: mută un produs din favorite direct în coșul de cumpărături prin POST

Toate acțiunile care modifică date necesită autentificare (@login_required) și cerere POST.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import Produs
from .models import ArticolCos, Favorit


@login_required
def lista_favorite(request):
    """Afișează pagina cu toate produsele salvate de utilizator în Wishlist (R2.1)."""
    # Pasul 1: Preluăm produsele favorite ale clientului logat, ordonate descrescător după data salvării
    favorite = Favorit.objects.filter(
        utilizator=request.user
    ).select_related('produs', 'produs__categorie', 'produs__furnizor')

    context = {
        'favorite': favorite,
        'titlu': 'Produse Favorite (Wishlist)',
    }
    return render(request, 'cumparaturi/favorite.html', context)


@login_required
def adauga_elimina_favorit(request, produs_id):
    """Comută starea de favorit a unui produs (adaugă dacă nu există, șterge dacă există).

    Se apelează prin POST de pe cardurile din catalog sau din pagina de detaliu.
    """
    if request.method != 'POST':
        messages.warning(request, "Această acțiune se realizează exclusiv prin butonul dedicat.")
        return redirect('catalog:acasa')

    # Pasul 1: Căutăm produsul
    produs = get_object_or_404(Produs, pk=produs_id, activ=True)

    # Pasul 2: Verificăm dacă este deja în favoritele utilizatorului
    favorit_existent = Favorit.objects.filter(utilizator=request.user, produs=produs).first()

    if favorit_existent:
        favorit_existent.delete()
        messages.info(request, f"Produsul «{produs.nume}» a fost eliminat din lista ta de favorite.")
    else:
        Favorit.objects.create(utilizator=request.user, produs=produs)
        messages.success(request, f"Produsul «{produs.nume}» a fost adăugat cu succes în Favorite!")

    # Pasul 3: Redirecționăm înapoi pe pagina de unde a venit cererea
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('cumparaturi:lista_favorite')


@login_required
def elimina_favorit(request, favorit_id):
    """Șterge un element din lista de favorite pe baza ID-ului înregistrării."""
    if request.method != 'POST':
        messages.warning(request, "Ștergerea din favorite se face doar prin cerere de tip POST.")
        return redirect('cumparaturi:lista_favorite')

    # Pasul 1: Preluăm articolul asigurându-ne că aparține utilizatorului curent
    favorit = get_object_or_404(Favorit, pk=favorit_id, utilizator=request.user)
    nume_produs = favorit.produs.nume
    favorit.delete()

    messages.info(request, f"Produsul «{nume_produs}» a fost eliminat din lista de favorite.")
    return redirect('cumparaturi:lista_favorite')


@login_required
def muta_in_cos(request, favorit_id):
    """Mută un produs din lista de favorite direct în coșul de cumpărături.

    Verifică stocul disponibil: dacă stocul > 0, adaugă în ArticolCos și șterge din Favorit.
    """
    if request.method != 'POST':
        messages.warning(request, "Acțiunea se realizează exclusiv prin cerere POST.")
        return redirect('cumparaturi:lista_favorite')

    # Pasul 1: Preluăm articolul favorit al utilizatorului
    favorit = get_object_or_404(Favorit, pk=favorit_id, utilizator=request.user)
    produs = favorit.produs

    # Pasul 2: Verificăm stocul produsului
    if not produs.in_stoc:
        messages.error(request, f"Produsul «{produs.nume}» nu poate fi mutat în coș deoarece este epuizat din stoc.")
        return redirect('cumparaturi:lista_favorite')

    # Pasul 3: Adăugăm în coș (sau mărim cantitatea dacă e deja prezent)
    articol_cos, creat = ArticolCos.objects.get_or_create(
        utilizator=request.user,
        produs=produs,
        defaults={'cantitate': 1}
    )
    if not creat:
        if articol_cos.cantitate < produs.stoc:
            articol_cos.cantitate += 1
            articol_cos.save()
        else:
            messages.warning(request, f"Cantitatea din coș a atins deja stocul maxim disponibil ({produs.stoc} buc.).")
            return redirect('cumparaturi:lista_favorite')

    # Pasul 4: Eliminăm produsul din favorite
    favorit.delete()

    messages.success(request, f"Produsul «{produs.nume}» a fost mutat cu succes în coșul tău de cumpărături!")
    return redirect('cumparaturi:lista_favorite')
