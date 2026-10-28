"""
catalog/views.py

Controllere (views) pentru răsfoirea catalogului de produse de către public și clienți:
- acasa: afișează secțiunea de bun venit, categoriile principale și cele mai recente produse
- lista_produse: catalogul complet cu căutare (după nume/descriere) și paginare (12/pagină)
- produse_categorie: produsele active dintr-o anumită categorie
- detaliu_produs: pagina individuală a produsului conform cerinței R1.3
"""

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from .models import Categorie, Produs


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
    """Afișează lista tuturor produselor active, cu suport pentru căutare și paginare.

    Cerința R1.4: Răsfoire produse și căutare simplă după cuvinte cheie.
    """
    # Pasul 1: Preluăm termenul de căutare din parametrul URL (?q=...)
    termen_cautare = request.GET.get('q', '').strip()

    # Pasul 2: Filtrăm doar produsele active (activ=True)
    produse_qs = Produs.objects.filter(activ=True).select_related('categorie', 'furnizor')

    # Pasul 3: Dacă utilizatorul a introdus un termen de căutare, filtrăm după nume sau descriere
    if termen_cautare:
        produse_qs = produse_qs.filter(
            Q(nume__icontains=termen_cautare) | Q(descriere__icontains=termen_cautare)
        )

    # Pasul 4: Paginare: câte 12 produse pe pagină
    paginator = Paginator(produse_qs, 12)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    context = {
        'page_obj': page_obj,
        'produse': page_obj.object_list,
        'termen_cautare': termen_cautare,
        'total_rezultate': paginator.count,
        'titlu': f"Căutare: {termen_cautare}" if termen_cautare else "Toate Produsele",
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
    ).select_related('furnizor')

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

    Cerința R1.3: Conține nume, descriere, specificații (tabel), preț, stoc,
    furnizor, modalități de livrare și categorie.
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
    ).exclude(pk=produs.pk)[:4]

    context = {
        'produs': produs,
        'specificatii': specificatii,
        'modalitati_livrare': modalitati_livrare,
        'produse_similare': produse_similare,
        'titlu': produs.nume,
    }
    return render(request, 'catalog/detaliu_produs.html', context)
