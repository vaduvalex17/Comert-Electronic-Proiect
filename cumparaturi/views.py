"""
cumparaturi/views.py

Controllere (views) pentru cumpărături:
1. Favorite (R2.1): vizualizare, adăugare/eliminare toggle, mutare în coș
2. Coș de cumpărături (R2.2):
   - vizualizare_cos: sumar comandă, calcul subtotal, intersecție modalități de livrare, cost transport, total
   - adaugare_in_cos: adăugare produs respectând stocul disponibil
   - actualizeaza_cos: modificare cantitate cu plafonare automată la stoc
   - elimina_din_cos: ștergere articol din coș
"""

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import ModalitateLivrare, Produs
from .models import ArticolCos, Favorit


# =====================================================================
# SECȚIUNEA 1: LISTA DE FAVORITE / WISHLIST (R2.1)
# =====================================================================

@login_required
def lista_favorite(request):
    """Afișează pagina cu toate produsele salvate de utilizator în Wishlist (R2.1)."""
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
    """Comută starea de favorit a unui produs (adaugă dacă nu există, șterge dacă există)."""
    if request.method != 'POST':
        messages.warning(request, "Această acțiune se realizează exclusiv prin butonul dedicat.")
        return redirect('catalog:acasa')

    produs = get_object_or_404(Produs, pk=produs_id, activ=True)
    favorit_existent = Favorit.objects.filter(utilizator=request.user, produs=produs).first()

    if favorit_existent:
        favorit_existent.delete()
        messages.info(request, f"Produsul «{produs.nume}» a fost eliminat din lista ta de favorite.")
    else:
        Favorit.objects.create(utilizator=request.user, produs=produs)
        messages.success(request, f"Produsul «{produs.nume}» a fost adăugat cu succes în Favorite!")

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

    favorit = get_object_or_404(Favorit, pk=favorit_id, utilizator=request.user)
    nume_produs = favorit.produs.nume
    favorit.delete()

    messages.info(request, f"Produsul «{nume_produs}» a fost eliminat din lista de favorite.")
    return redirect('cumparaturi:lista_favorite')


@login_required
def muta_in_cos(request, favorit_id):
    """Mută un produs din lista de favorite direct în coșul de cumpărături."""
    if request.method != 'POST':
        messages.warning(request, "Acțiunea se realizează exclusiv prin cerere POST.")
        return redirect('cumparaturi:lista_favorite')

    favorit = get_object_or_404(Favorit, pk=favorit_id, utilizator=request.user)
    produs = favorit.produs

    if not produs.in_stoc:
        messages.error(request, f"Produsul «{produs.nume}» nu poate fi mutat în coș deoarece este epuizat din stoc.")
        return redirect('cumparaturi:lista_favorite')

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

    favorit.delete()
    messages.success(request, f"Produsul «{produs.nume}» a fost mutat cu succes în coșul tău de cumpărături!")
    return redirect('cumparaturi:vizualizare_cos')


# =====================================================================
# SECȚIUNEA 2: COȘUL DE CUMPĂRĂTURI (R2.2 — Prima parte)
# =====================================================================

@login_required
def vizualizare_cos(request):
    """Afișează coșul de cumpărături curent, sumarul comenzii și opțiunile de livrare.

    Cerința R2.2:
    - subtotal produse
    - calcul modalități de livrare comune (intersecția tuturor produselor din coș conform §6.1)
    - cost livrare și total general calculat strict pe server
    """
    # Pasul 1: Preluăm articolele din coșul utilizatorului
    articole = ArticolCos.objects.filter(
        utilizator=request.user
    ).select_related('produs', 'produs__categorie')

    # Pasul 2: Calculăm subtotalul produselor
    subtotal = sum(articol.subtotal for articol in articole)

    # Pasul 3: Calculăm intersecția modalităților de livrare
    # Sunt oferite doar modalitățile compatibile cu TOATE produsele din coș
    livrari_comune = []
    if articole.exists():
        qs_livrari = ModalitateLivrare.objects.all()
        for art in articole:
            qs_livrari = qs_livrari.filter(produse=art.produs)
        livrari_comune = list(qs_livrari.distinct().order_by('cost'))

    # Pasul 4: Determinăm modalitatea de livrare selectată
    livrare_id_cerut = request.GET.get('livrare') or request.session.get('livrare_id')
    livrare_selectata = None

    if livrare_id_cerut and livrari_comune:
        for liv in livrari_comune:
            if str(liv.id) == str(livrare_id_cerut):
                livrare_selectata = liv
                request.session['livrare_id'] = liv.id
                break

    # Dacă nu a fost selectată una validă, o alegem pe prima (cea mai ieftină)
    if not livrare_selectata and livrari_comune:
        livrare_selectata = livrari_comune[0]
        request.session['livrare_id'] = livrare_selectata.id

    cost_livrare = livrare_selectata.cost if livrare_selectata else Decimal('0.00')
    total = subtotal + cost_livrare

    context = {
        'articole': articole,
        'subtotal': subtotal,
        'livrari_comune': livrari_comune,
        'livrare_selectata': livrare_selectata,
        'cost_livrare': cost_livrare,
        'total': total,
        'titlu': 'Coșul Meu de Cumpărături',
    }
    return render(request, 'cumparaturi/cos.html', context)


@login_required
def adaugare_in_cos(request, produs_id):
    """Adaugă un produs în coșul utilizatorului, respectând stocul existent (R2.2)."""
    if request.method != 'POST':
        messages.warning(request, "Adăugarea în coș se realizează prin apăsarea butonului din pagină.")
        return redirect('catalog:acasa')

    # Pasul 1: Căutăm produsul activ
    produs = get_object_or_404(Produs, pk=produs_id, activ=True)

    # Pasul 2: Preluăm cantitatea dorită (implicit 1)
    try:
        cantitate_ceruta = int(request.POST.get('cantitate', 1))
        if cantitate_ceruta < 1:
            cantitate_ceruta = 1
    except ValueError:
        cantitate_ceruta = 1

    # Pasul 3: Verificăm dacă produsul este în stoc
    if produs.stoc <= 0:
        messages.error(request, f"Produsul «{produs.nume}» este epuizat din stoc.")
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or 'catalog:lista_produse')

    # Pasul 4: Preluăm sau creăm articolul din coș
    articol_cos, creat = ArticolCos.objects.get_or_create(
        utilizator=request.user,
        produs=produs,
        defaults={'cantitate': 0}
    )

    cantitate_noua = articol_cos.cantitate + cantitate_ceruta

    # Pasul 5: Plafonăm cantitatea la stocul maxim disponibil
    if cantitate_noua > produs.stoc:
        articol_cos.cantitate = produs.stoc
        articol_cos.save()
        messages.warning(
            request,
            f"Stoc limitat! Am adăugat cantitatea maximă disponibilă ({produs.stoc} buc.) pentru «{produs.nume}»."
        )
    else:
        articol_cos.cantitate = cantitate_noua
        articol_cos.save()
        messages.success(request, f"Produsul «{produs.nume}» a fost adăugat în coș!")

    # Redirecționăm utilizatorul către pagina coșului
    return redirect('cumparaturi:vizualizare_cos')


@login_required
def actualizeaza_cos(request, articol_id):
    """Actualizează cantitatea unui produs din coș (R2.2)."""
    if request.method != 'POST':
        return redirect('cumparaturi:vizualizare_cos')

    # Pasul 1: Preluăm articolul din coș aparținând utilizatorului logat
    articol = get_object_or_404(ArticolCos, pk=articol_id, utilizator=request.user)

    # Pasul 2: Validăm cantitatea transmisă
    try:
        cantitate = int(request.POST.get('cantitate', 1))
    except ValueError:
        cantitate = 1

    nume_produs = articol.produs.nume
    stoc_disponibil = articol.produs.stoc

    # Pasul 3: Dacă cantitatea este <= 0, eliminăm produsul din coș
    if cantitate <= 0:
        articol.delete()
        messages.info(request, f"Produsul «{nume_produs}» a fost eliminat din coș.")
        return redirect('cumparaturi:vizualizare_cos')

    # Pasul 4: Plafonăm la stocul existent
    if cantitate > stoc_disponibil:
        articol.cantitate = stoc_disponibil
        articol.save()
        messages.warning(
            request,
            f"Stoc insuficient pentru «{nume_produs}». Cantitatea a fost ajustată la stocul maxim ({stoc_disponibil} buc.)."
        )
    else:
        articol.cantitate = cantitate
        articol.save()
        messages.success(request, f"Cantitatea pentru «{nume_produs}» a fost actualizată la {cantitate} buc.")

    return redirect('cumparaturi:vizualizare_cos')


@login_required
def elimina_din_cos(request, articol_id):
    """Elimină complet un produs din coșul utilizatorului (R2.2)."""
    if request.method != 'POST':
        return redirect('cumparaturi:vizualizare_cos')

    articol = get_object_or_404(ArticolCos, pk=articol_id, utilizator=request.user)
    nume_produs = articol.produs.nume
    articol.delete()

    messages.info(request, f"Produsul «{nume_produs}» a fost șters din coșul tău.")
    return redirect('cumparaturi:vizualizare_cos')
