"""
cumparaturi/views.py

Controllere (views) pentru întregul flux de cumpărături:
1. Favorite (R2.1): vizualizare listă, toggle adăugare/eliminare, mutare în coș
2. Coș de cumpărături (R2.2): vizualizare, adăugare, actualizare cantitate, ștergere
3. Finalizare comandă (R2.2): checkout, validare adresă și card, tranzacție atomică prin servicii.py
4. Confirmare comandă (R2.2): sumarul final după plasarea cu succes a achiziției
5. Istoric comenzi (R2.3):
   - istoric_comenzi: lista comenzilor proprii ale clientului
   - detaliu_comanda: detaliul complet al unei comenzi (cu protecție 404 pentru comenzile altora)
   - admin_comenzi_lista: panou admin pentru vizualizarea tuturor comenzilor și schimbarea statusului
"""

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import ModalitateLivrare, Produs
from conturi.decoratori import doar_admin
from .forms import FinalizareComandaForm
from .models import ArticolCos, CodReducere, Comanda, Favorit
from .servicii import StocInsuficient, plaseaza_comanda


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
    """Afișează coșul de cumpărături curent, sumarul comenzii, codul de reducere și opțiunile de livrare."""
    articole = ArticolCos.objects.filter(
        utilizator=request.user
    ).select_related('produs', 'produs__categorie')

    subtotal = sum(articol.subtotal for articol in articole)

    # Verificăm dacă există un cod promoțional activ în sesiune (Bonus Faza 9)
    cod_salvat = request.session.get('cod_reducere')
    cupon = None
    valoare_reducere = Decimal('0.00')

    if cod_salvat and subtotal > Decimal('0.00'):
        cupon = CodReducere.objects.filter(cod=cod_salvat, activ=True).first()
        if cupon:
            este_valid, motiv = cupon.este_valid(subtotal)
            if este_valid:
                valoare_reducere = cupon.calculeaza_reducere(subtotal)
            else:
                # Nu mai este valid pentru suma actuală (ex: s-a redus cantitatea sub pragul minim)
                request.session.pop('cod_reducere', None)
                messages.warning(request, f"Codul «{cod_salvat}» a fost anulat: {motiv}")
                cupon = None
        else:
            request.session.pop('cod_reducere', None)

    # Intersecția modalităților de livrare (§6.1)
    livrari_comune = []
    if articole.exists():
        qs_livrari = ModalitateLivrare.objects.all()
        for art in articole:
            qs_livrari = qs_livrari.filter(produse=art.produs)
        livrari_comune = list(qs_livrari.distinct().order_by('cost'))

    livrare_id_cerut = request.GET.get('livrare') or request.session.get('livrare_id')
    livrare_selectata = None

    if livrare_id_cerut and livrari_comune:
        for liv in livrari_comune:
            if str(liv.id) == str(livrare_id_cerut):
                livrare_selectata = liv
                request.session['livrare_id'] = liv.id
                break

    if not livrare_selectata and livrari_comune:
        livrare_selectata = livrari_comune[0]
        request.session['livrare_id'] = livrare_selectata.id

    cost_livrare = livrare_selectata.cost if livrare_selectata else Decimal('0.00')
    total = (subtotal - valoare_reducere) + cost_livrare

    context = {
        'articole': articole,
        'subtotal': subtotal,
        'cupon': cupon,
        'valoare_reducere': valoare_reducere,
        'livrari_comune': livrari_comune,
        'livrare_selectata': livrare_selectata,
        'cost_livrare': cost_livrare,
        'total': total,
        'titlu': 'Coșul Meu de Cumpărături',
    }
    return render(request, 'cumparaturi/cos.html', context)


@login_required
def aplica_cod_reducere(request):
    """Validează și aplică un cod promoțional în sesiunea cumpărătorului (Bonus Faza 9)."""
    if request.method != 'POST':
        return redirect('cumparaturi:vizualizare_cos')

    cod_introdus = request.POST.get('cod', '').strip().upper()
    if not cod_introdus:
        messages.error(request, "Te rugăm să introduci un cod promoțional.")
        return redirect('cumparaturi:vizualizare_cos')

    articole = ArticolCos.objects.filter(utilizator=request.user).select_related('produs')
    subtotal = sum(art.subtotal for art in articole)

    if subtotal <= Decimal('0.00'):
        messages.warning(request, "Coșul este gol. Adaugă produse înainte de a aplica un cod promoțional.")
        return redirect('cumparaturi:vizualizare_cos')

    cupon = CodReducere.objects.filter(cod=cod_introdus).first()
    if not cupon:
        messages.error(request, f"Codul promoțional «{cod_introdus}» nu există sau este incorect.")
        return redirect('cumparaturi:vizualizare_cos')

    este_valid, mesaj = cupon.este_valid(subtotal)
    if not este_valid:
        messages.error(request, mesaj)
        return redirect('cumparaturi:vizualizare_cos')

    request.session['cod_reducere'] = cupon.cod
    reducere_estimata = cupon.calculeaza_reducere(subtotal)
    messages.success(
        request,
        f"Felicitări! Codul «{cupon.cod}» a fost aplicat cu succes. "
        f"Ai obținut o reducere de {cupon.procent_reducere}% (-{reducere_estimata} lei)."
    )
    return redirect('cumparaturi:vizualizare_cos')


@login_required
def elimina_cod_reducere(request):
    """Elimină codul promoțional curent din sesiune."""
    if request.method == 'POST':
        cod_sters = request.session.pop('cod_reducere', None)
        if cod_sters:
            messages.info(request, f"Codul promoțional «{cod_sters}» a fost eliminat din coș.")
    return redirect('cumparaturi:vizualizare_cos')


@login_required
def adaugare_in_cos(request, produs_id):
    """Adaugă un produs în coșul utilizatorului, respectând stocul existent (R2.2)."""
    if request.method != 'POST':
        messages.warning(request, "Adăugarea în coș se realizează prin apăsarea butonului din pagină.")
        return redirect('catalog:acasa')

    produs = get_object_or_404(Produs, pk=produs_id, activ=True)

    try:
        cantitate_ceruta = int(request.POST.get('cantitate', 1))
        if cantitate_ceruta < 1:
            cantitate_ceruta = 1
    except ValueError:
        cantitate_ceruta = 1

    if produs.stoc <= 0:
        messages.error(request, f"Produsul «{produs.nume}» este epuizat din stoc.")
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or 'catalog:lista_produse')

    articol_cos, creat = ArticolCos.objects.get_or_create(
        utilizator=request.user,
        produs=produs,
        defaults={'cantitate': 0}
    )

    cantitate_noua = articol_cos.cantitate + cantitate_ceruta

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

    return redirect('cumparaturi:vizualizare_cos')


@login_required
def actualizeaza_cos(request, articol_id):
    """Actualizează cantitatea unui produs din coș (R2.2)."""
    if request.method != 'POST':
        return redirect('cumparaturi:vizualizare_cos')

    articol = get_object_or_404(ArticolCos, pk=articol_id, utilizator=request.user)

    try:
        cantitate = int(request.POST.get('cantitate', 1))
    except ValueError:
        cantitate = 1

    nume_produs = articol.produs.nume
    stoc_disponibil = articol.produs.stoc

    if cantitate <= 0:
        articol.delete()
        messages.info(request, f"Produsul «{nume_produs}» a fost eliminat din coș.")
        return redirect('cumparaturi:vizualizare_cos')

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


# =====================================================================
# SECȚIUNEA 3: FINALIZARE ȘI CONFIRMARE COMANDĂ (R2.2 — A doua parte)
# =====================================================================

@login_required
def finalizare_comanda(request):
    """Formularul de checkout pentru plasarea comenzii (Cerința R2.2)."""
    articole = list(
        ArticolCos.objects.filter(utilizator=request.user).select_related('produs')
    )
    if not articole:
        messages.warning(request, "Coșul tău este gol. Adaugă cel puțin un produs înainte de a finaliza o comandă.")
        return redirect('cumparaturi:vizualizare_cos')

    qs_livrari = ModalitateLivrare.objects.all()
    for art in articole:
        qs_livrari = qs_livrari.filter(produse=art.produs)
    livrari_comune = qs_livrari.distinct().order_by('cost')

    if not livrari_comune.exists():
        messages.error(
            request,
            "Produsele din coșul tău au modalități de livrare incompatibile. "
            "Te rugăm să ajustezi produsele din coș."
        )
        return redirect('cumparaturi:vizualizare_cos')

    subtotal = sum(art.subtotal for art in articole)

    # Verificăm dacă există cupon activ în sesiune (Bonus Faza 9)
    cod_salvat = request.session.get('cod_reducere')
    cupon = None
    valoare_reducere = Decimal('0.00')
    if cod_salvat:
        cupon = CodReducere.objects.filter(cod=cod_salvat, activ=True).first()
        if cupon:
            este_valid, _ = cupon.este_valid(subtotal)
            if este_valid:
                valoare_reducere = cupon.calculeaza_reducere(subtotal)
            else:
                cupon = None

    if request.method == 'POST':
        formular = FinalizareComandaForm(livrari_comune, request.POST)
        if formular.is_valid():
            try:
                comanda = plaseaza_comanda(
                    utilizator=request.user,
                    date_livrare=formular.cleaned_data,
                    modalitate_livrare=formular.cleaned_data['modalitate_livrare'],
                    numar_card=formular.cleaned_data['numar_card'],
                    cod_reducere_obj=cupon
                )
                # Ștergem cuponul consumat din sesiune
                request.session.pop('cod_reducere', None)
                messages.success(request, f"Comanda ta #{comanda.id} a fost înregistrată cu succes!")
                return redirect('cumparaturi:confirmare_comanda', comanda_id=comanda.id)

            except StocInsuficient as eroare_stoc:
                messages.error(request, str(eroare_stoc))
            except ValueError as eroare_val:
                messages.error(request, str(eroare_val))
        else:
            messages.error(request, "Formularul conține erori. Te rugăm să verifici datele introduse.")
    else:
        nume_implicit = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        livrare_initiala_id = request.session.get('livrare_id')
        livrare_initiala = None
        if livrare_initiala_id:
            livrare_initiala = livrari_comune.filter(id=livrare_initiala_id).first()

        formular = FinalizareComandaForm(
            livrari_permise=livrari_comune,
            initial={
                'nume_destinatar': nume_implicit,
                'titular_card': nume_implicit.upper(),
                'modalitate_livrare': livrare_initiala or livrari_comune.first(),
            }
        )

    context = {
        'form': formular,
        'articole': articole,
        'subtotal': subtotal,
        'cupon': cupon,
        'valoare_reducere': valoare_reducere,
        'livrari_comune': livrari_comune,
        'titlu': 'Finalizare Comandă (Checkout)',
    }
    return render(request, 'cumparaturi/finalizare.html', context)


@login_required
def confirmare_comanda(request, comanda_id):
    """Afișează pagina de confirmare („Mulțumim pentru comandă”) pentru o comandă plasată (R2.2)."""
    comanda = get_object_or_404(
        Comanda.objects.prefetch_related('articole'),
        id=comanda_id,
        utilizator=request.user
    )

    context = {
        'comanda': comanda,
        'articole': comanda.articole.all(),
        'titlu': f"Confirmare Comandă #{comanda.id}",
    }
    return render(request, 'cumparaturi/confirmare.html', context)


# =====================================================================
# SECȚIUNEA 4: ISTORIC COMENZI & ADMINISTRARE COMENZI (R2.3)
# =====================================================================

@login_required
def istoric_comenzi(request):
    """Afișează lista comenzilor plasate de utilizatorul autentificat (Cerința R2.3)."""
    # Pasul 1: Clientul își vede STRICT comenzile proprii
    comenzi_qs = Comanda.objects.filter(
        utilizator=request.user
    ).prefetch_related('articole').order_by('-creata_la')

    # Pasul 2: Paginăm lista (10 comenzi pe pagină)
    paginator = Paginator(comenzi_qs, 10)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    context = {
        'page_obj': page_obj,
        'comenzi': page_obj.object_list,
        'total_comenzi': paginator.count,
        'titlu': 'Istoricul Comenzilor Mele',
    }
    return render(request, 'cumparaturi/istoric_comenzi.html', context)


@login_required
def detaliu_comanda(request, comanda_id):
    """Afișează factura și detaliile complete ale unei comenzi trecute (Cerința R2.3).

    Securitate esențială conform §6.2: filtrăm strict după `utilizator=request.user`.
    Dacă un client încearcă să vadă comanda altcuiva introducând un alt ID în URL, primește 404.
    """
    comanda = get_object_or_404(
        Comanda.objects.prefetch_related('articole', 'articole__produs'),
        id=comanda_id,
        utilizator=request.user
    )

    context = {
        'comanda': comanda,
        'articole': comanda.articole.all(),
        'titlu': f"Detaliu Comandă #{comanda.id}",
    }
    return render(request, 'cumparaturi/detaliu_comanda.html', context)


@doar_admin
def admin_comenzi_lista(request):
    """Panoul de administrare cu toate comenzile plasate de toți clienții (bonus demo)."""
    comenzi_qs = Comanda.objects.select_related('utilizator', 'modalitate_livrare').order_by('-creata_la')

    # Filtrare după status
    status_selectat = request.GET.get('status', '').strip()
    if status_selectat:
        comenzi_qs = comenzi_qs.filter(status=status_selectat)

    paginator = Paginator(comenzi_qs, 15)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    context = {
        'page_obj': page_obj,
        'comenzi': page_obj.object_list,
        'total_comenzi': paginator.count,
        'status_selectat': status_selectat,
        'status_alegeri': Comanda.STATUS_ALEGERI,
        'titlu': 'Administrare Comenzi Clienți',
    }
    return render(request, 'cumparaturi/admin/admin_comenzi_lista.html', context)


@doar_admin
def admin_comanda_status(request, comanda_id):
    """Permite administratorului să actualizeze statusul unei comenzi (POST)."""
    if request.method != 'POST':
        return redirect('cumparaturi:admin_comenzi_lista')

    comanda = get_object_or_404(Comanda, id=comanda_id)
    status_nou = request.POST.get('status')

    statusuri_valide = [s[0] for s in Comanda.STATUS_ALEGERI]
    if status_nou in statusuri_valide:
        comanda.status = status_nou
        comanda.save()
        messages.success(request, f"Statusul comenzii #{comanda.id} a fost schimbat în «{comanda.get_status_display()}».")
    else:
        messages.error(request, "Statusul specificat este invalid.")

    return redirect('cumparaturi:admin_comenzi_lista')
