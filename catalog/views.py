"""
catalog/views.py

Controllere (views) pentru răsfoirea catalogului de produse de către public și clienți:
- acasa: afișează secțiunea de bun venit, categoriile principale și cele mai recente produse
- lista_produse: catalogul complet cu căutare (după nume/descriere) și paginare (12/pagină)
- produse_categorie: produsele active dintr-o anumită categorie
- detaliu_produs: pagina individuală a produsului conform cerinței R1.3
"""

from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from cumparaturi.models import ArticolComanda
from .forms import RecenzieForm
from .models import Categorie, Furnizor, ModalitateLivrare, Produs, Recenzie


def acasa(request):
    """Afișează pagina principală a magazinului (Acasă).

    Prezintă categoriile comerciale disponibile și cele mai recente 8 produse active.
    """
    # Pasul 1: Preluăm categoriile care au produse active
    categorii = Categorie.objects.annotate(
        numar_produse=Count('produse', filter=Q(produse__activ=True))
    ).order_by('nume')

    # Pasul 2: Preluăm ultimele 8 produse active adăugate în magazin
    produse_recente = Produs.objects.filter(activ=True).select_related('categorie')[:8]

    # Pasul 3: Construim contextul transmis către template
    context = {
        'categorii': categorii,
        'produse_recente': produse_recente,
        'titlu': 'Acasă — ElectroMag',
    }
    return render(request, 'catalog/acasa.html', context)


def lista_produse(request):
    """Afișează lista produselor active, cu căutare, paginare și filtrare avansată (ȘI / SAU).

    Cerința R1.4 + Faza 9 (Bonus Filtrare Avansată):
    - Căutare text (nume / descriere)
    - Filtrare pe categorie, furnizor, interval de preț (min-max), disponibilitate în stoc și metodă de livrare
    - Operator logic configurabil între criterii: ȘI (AND) sau SAU (OR)
    - Sortare după preț (crescător / descrescător), denumire sau data adăugării
    """
    # 1. Preluarea parametrilor din cererea GET
    termen_cautare = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '').strip()
    furnizor_id = request.GET.get('furnizor', '').strip()
    pret_min = request.GET.get('pret_min', '').strip()
    pret_max = request.GET.get('pret_max', '').strip()
    in_stoc_doar = request.GET.get('in_stoc', '').strip() in ('1', 'true', 'on')
    livrare_id = request.GET.get('livrare', '').strip()
    operator_logic = request.GET.get('operator', 'si').strip().lower()
    sortare = request.GET.get('sortare', 'nou').strip()

    # 2. Interogarea de bază: doar produsele active din magazin
    produse_qs = Produs.objects.filter(activ=True).select_related(
        'categorie', 'furnizor'
    ).prefetch_related('modalitati_livrare')

    # 3. Construim lista de condiții Q pentru fiecare filtru completat
    conditii = []

    if termen_cautare:
        conditii.append(
            Q(nume__icontains=termen_cautare) | Q(descriere__icontains=termen_cautare)
        )

    if categorie_id.isdigit():
        conditii.append(Q(categorie_id=int(categorie_id)))

    if furnizor_id.isdigit():
        conditii.append(Q(furnizor_id=int(furnizor_id)))

    if pret_min:
        try:
            valoare_min = Decimal(pret_min.replace(',', '.'))
            conditii.append(Q(pret__gte=valoare_min))
        except (InvalidOperation, ValueError):
            pass

    if pret_max:
        try:
            valoare_max = Decimal(pret_max.replace(',', '.'))
            conditii.append(Q(pret__lte=valoare_max))
        except (InvalidOperation, ValueError):
            pass

    if in_stoc_doar:
        conditii.append(Q(stoc__gt=0))

    if livrare_id.isdigit():
        conditii.append(Q(modalitati_livrare__id=int(livrare_id)))

    # 4. Aplicăm operatorul logic între criterii (ȘI vs SAU)
    if conditii:
        if operator_logic == 'sau':
            # Operator SAU (OR): produsul respectă cel puțin unul dintre filtrele bifate
            filtru_sau = conditii[0]
            for c in conditii[1:]:
                filtru_sau |= c
            produse_qs = produse_qs.filter(filtru_sau)
        else:
            # Operator ȘI (AND): produsul respectă simultan toate filtrele aplicate
            for c in conditii:
                produse_qs = produse_qs.filter(c)

    # Distinct pentru a preveni duplicatele datorate join-ului cu modalitati_livrare
    produse_qs = produse_qs.distinct()

    # 5. Aplicăm sortarea
    if sortare == 'pret_asc':
        produse_qs = produse_qs.order_by('pret')
    elif sortare == 'pret_desc':
        produse_qs = produse_qs.order_by('-pret')
    elif sortare == 'nume':
        produse_qs = produse_qs.order_by('nume')
    else:
        produse_qs = produse_qs.order_by('-creat_la')

    # 6. Construim parametrul URL pentru paginare fără a pierde filtrele
    parametri_get = request.GET.copy()
    if 'pagina' in parametri_get:
        del parametri_get['pagina']
    parametri_url = parametri_get.urlencode()

    # 7. Paginare: câte 12 produse pe pagină
    paginator = Paginator(produse_qs, 12)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    # 8. Date de suport pentru controalele din formularul de filtrare
    toate_categoriile = Categorie.objects.all().order_by('nume')
    toti_furnizorii = Furnizor.objects.all().order_by('nume')
    toate_livrarile = ModalitateLivrare.objects.all().order_by('cost')

    context = {
        'page_obj': page_obj,
        'produse': page_obj.object_list,
        'termen_cautare': termen_cautare,
        'total_rezultate': paginator.count,
        'parametri_url': parametri_url,
        # Liste pentru selecție
        'categorii': toate_categoriile,
        'furnizori': toti_furnizorii,
        'modalitati_livrare': toate_livrarile,
        # Starea filtrelor curente
        'categorie_selectata': int(categorie_id) if categorie_id.isdigit() else None,
        'furnizor_selectat': int(furnizor_id) if furnizor_id.isdigit() else None,
        'livrare_selectata': int(livrare_id) if livrare_id.isdigit() else None,
        'pret_min': pret_min,
        'pret_max': pret_max,
        'in_stoc_doar': in_stoc_doar,
        'operator_logic': operator_logic,
        'sortare': sortare,
        'are_filtre_active': bool(conditii),
        'titlu': f"Căutare: {termen_cautare}" if termen_cautare else "Catalog Produse",
    }
    return render(request, 'catalog/lista_produse.html', context)


def produse_categorie(request, slug):
    """Afișează toate produsele active asociate unei categorii selectate.

    Cerința R1.4: Răsfoire produse pe categorii.
    """
    # Pasul 1: Căutăm categoria după slug sau returnăm eroare 404 dacă nu există
    categorie = get_object_or_404(Categorie, slug=slug)

    # Pasul 2: Preluăm produsele active din categoria respectivă
    produse_qs = Produs.objects.filter(
        categorie=categorie,
        activ=True
    ).select_related('categorie', 'furnizor')

    # Pasul 3: Paginare pentru categoria selectată (12 produse pe pagină)
    paginator = Paginator(produse_qs, 12)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    context = {
        'categorie': categorie,
        'page_obj': page_obj,
        'produse': page_obj.object_list,
        'total_rezultate': paginator.count,
        'titlu': f"Categoria: {categorie.nume}",
    }
    return render(request, 'catalog/produse_categorie.html', context)


def detaliu_produs(request, slug):
    """Afișează pagina cu informațiile complete despre un produs.

    Cerința R1.3 + Faza 9 (Bonus Recenzii & Rating):
    - Conține nume, descriere, specificații (tabel), preț, stoc, furnizor, livrări și categorie
    - Afișează recenziile clienților și formularul dedicat strict cumpărătorilor verificați
    """
    # Pasul 1: Căutăm produsul după slug, asigurându-ne că este activ
    produs = get_object_or_404(
        Produs.objects.select_related('categorie', 'furnizor').prefetch_related('modalitati_livrare'),
        slug=slug,
        activ=True
    )

    # Pasul 2: Preluăm specificațiile structurate (perechi cheie-valoare)
    specificatii = produs.specificatii_lista()

    # Pasul 3: Preluăm modalitățile de livrare compatibile
    modalitati_livrare = produs.modalitati_livrare.all()

    # Pasul 4: Preluăm câteva produse similare din aceeași categorie (exclusiv cel curent)
    produse_similare = Produs.objects.filter(
        categorie=produs.categorie,
        activ=True
    ).select_related('categorie').exclude(pk=produs.pk)[:4]

    # Pasul 5: Recenzii și verificare dacă utilizatorul este cumpărător verificat (Bonus Faza 9)
    recenzii = produs.recenzii.select_related('utilizator').order_by('-creata_la')
    poate_lasa_recenzie = False
    deja_recenzat = False

    if request.user.is_authenticated:
        deja_recenzat = recenzii.filter(utilizator=request.user).exists()
        if not deja_recenzat:
            # Clientul trebuie să fi cumpărat acest produs anterior
            a_cumparat = ArticolComanda.objects.filter(
                comanda__utilizator=request.user,
                produs=produs
            ).exists()
            poate_lasa_recenzie = a_cumparat

    form_recenzie = RecenzieForm() if poate_lasa_recenzie else None

    context = {
        'produs': produs,
        'specificatii': specificatii,
        'modalitati_livrare': modalitati_livrare,
        'produse_similare': produse_similare,
        'recenzii': recenzii,
        'poate_lasa_recenzie': poate_lasa_recenzie,
        'deja_recenzat': deja_recenzat,
        'form_recenzie': form_recenzie,
        'titlu': produs.nume,
    }
    return render(request, 'catalog/detaliu_produs.html', context)


@login_required
def adauga_recenzie(request, slug):
    """Înregistrează o recenzie pentru un produs dacă utilizatorul l-a cumpărat anterior (Bonus)."""
    if request.method != 'POST':
        return redirect('catalog:detaliu_produs', slug=slug)

    produs = get_object_or_404(Produs, slug=slug, activ=True)

    # 1. Verificare: cumpărător verificat
    a_cumparat = ArticolComanda.objects.filter(
        comanda__utilizator=request.user,
        produs=produs
    ).exists()
    if not a_cumparat:
        messages.error(
            request,
            "Doar clienții care au comandat și achiziționat acest produs pot lăsa o recenzie verificată."
        )
        return redirect('catalog:detaliu_produs', slug=slug)

    # 2. Verificare: nu a lăsat deja o recenzie
    if Recenzie.objects.filter(produs=produs, utilizator=request.user).exists():
        messages.warning(request, "Ai trimis deja o recenzie pentru acest produs.")
        return redirect('catalog:detaliu_produs', slug=slug)

    formular = RecenzieForm(request.POST)
    if formular.is_valid():
        recenzie = formular.save(commit=False)
        recenzie.produs = produs
        recenzie.utilizator = request.user
        recenzie.save()
        messages.success(request, "Recenzia ta a fost publicată cu succes! Mulțumim pentru feedback.")
    else:
        messages.error(request, "Formularul conține erori. Te rugăm să verifici datele completate.")

    return redirect('catalog:detaliu_produs', slug=slug)


def despre_noi(request):
    """Afișează pagina de prezentare a magazinului și a echipei (Bonus)."""
    return render(request, 'catalog/despre.html', {'titlu': 'Despre Noi — ElectroMag'})


def contact(request):
    """Afișează pagina de contact și asistență clienți (Bonus)."""
    return render(request, 'catalog/contact.html', {'titlu': 'Contact & Suport — ElectroMag'})
