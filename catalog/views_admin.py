"""
catalog/views_admin.py

Controllere (views) pentru administrarea produselor de către administratori (Cerința R1.2):
- admin_produse_lista: tabelul cu toate produsele (active și inactive), cu filtre și căutare
- admin_produs_adauga: formular de adăugare produs nou
- admin_produs_editeaza: actualizarea datelor unui produs existent
- admin_produs_sterge: ștergere sigură cu confirmare (soft-delete pentru produsele comandate)

Toate funcțiile sunt protejate cu decoratorul `@doar_admin`.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from conturi.decoratori import doar_admin
from cumparaturi.models import ArticolComanda
from .forms import ProdusForm
from .models import Produs


@doar_admin
def admin_produse_lista(request):
    """Afișează tabelul de administrare al tuturor produselor din baza de date.

    Permite administratorului să vadă atât produsele active, cât și pe cele dezactivate,
    să caute rapid un produs și să acceseze opțiunile de Editare / Ștergere.
    """
    # Pasul 1: Preluăm termenul opțional de căutare
    termen = request.GET.get('q', '').strip()

    # Pasul 2: Încărcăm produsele optimizat cu categorie și furnizor
    produse_qs = Produs.objects.select_related('categorie', 'furnizor').order_by('-creat_la')

    if termen:
        produse_qs = produse_qs.filter(
            Q(nume__icontains=termen) |
            Q(categorie__nume__icontains=termen) |
            Q(furnizor__nume__icontains=termen)
        )

    # Pasul 3: Paginăm produsele (15 produse pe pagină în panoul admin)
    paginator = Paginator(produse_qs, 15)
    numar_pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(numar_pagina)

    context = {
        'page_obj': page_obj,
        'produse': page_obj.object_list,
        'termen': termen,
        'total_produse': paginator.count,
        'titlu': 'Administrare Produse',
    }
    return render(request, 'catalog/admin/admin_produse_lista.html', context)


@doar_admin
def admin_produs_adauga(request):
    """Permite administratorului să adauge un produs nou în catalog (Cerința R1.2)."""
    # Pasul 1: La trimiterea formularului prin POST (cu suport pentru imagini: request.FILES)
    if request.method == 'POST':
        formular = ProdusForm(request.POST, request.FILES)
        if formular.is_valid():
            produs_creat = formular.save()
            messages.success(request, f"Produsul «{produs_creat.nume}» a fost adăugat cu succes în catalog!")
            return redirect('catalog:admin_produse_lista')
        else:
            messages.error(request, "Formularul conține erori. Te rugăm să verifici câmpurile marcate cu roșu.")
    else:
        # Pasul 2: Formular gol la accesarea prin GET
        formular = ProdusForm()

    context = {
        'form': formular,
        'titlu': 'Adaugă Produs Nou',
        'actiune': 'Adaugă',
    }
    return render(request, 'catalog/admin/admin_produs_formular.html', context)


@doar_admin
def admin_produs_editeaza(request, pk):
    """Permite administratorului să modifice datele unui produs existent (Cerința R1.2)."""
    # Pasul 1: Căutăm produsul după cheia primară (pk)
    produs = get_object_or_404(Produs, pk=pk)

    # Pasul 2: Procesăm modificările la trimiterea prin POST
    if request.method == 'POST':
        formular = ProdusForm(request.POST, request.FILES, instance=produs)
        if formular.is_valid():
            produs_salvat = formular.save()
            messages.success(request, f"Produsul «{produs_salvat.nume}» a fost actualizat cu succes!")
            return redirect('catalog:admin_produse_lista')
        else:
            messages.error(request, "Modificările nu au putut fi salvate din cauza unor erori de validare.")
    else:
        # Pasul 3: Populăm formularul cu valorile actuale ale produsului
        formular = ProdusForm(instance=produs)

    context = {
        'form': formular,
        'produs': produs,
        'titlu': f"Editează: {produs.nume}",
        'actiune': 'Salvează modificările',
    }
    return render(request, 'catalog/admin/admin_produs_formular.html', context)


@doar_admin
def admin_produs_sterge(request, pk):
    """Șterge un produs sau îl dezactivează (soft-delete) dacă a fost deja comandat.

    Regulă de business esențială:
    - Dacă produsul NU apare în nicio comandă: este șters fizic din baza de date.
    - Dacă produsul APARE în comenzi anterioare: este marcat `activ=False` (soft-delete)
      pentru ca istoricul facturilor clienților să rămână complet și integru.
    """
    # Pasul 1: Identificăm produsul dorit
    produs = get_object_or_404(Produs, pk=pk)

    # Pasul 2: Verificăm dacă produsul este inclus în comenzi trecute
    are_comenzi = ArticolComanda.objects.filter(produs=produs).exists()

    # Pasul 3: La confirmarea prin POST
    if request.method == 'POST':
        nume_produs = produs.nume
        if are_comenzi:
            # Soft-delete: doar îl dezactivăm
            produs.activ = False
            produs.save()
            messages.warning(
                request,
                f"Produsul «{nume_produs}» a fost dezactivat (soft-delete) deoarece apare în istoricul comenzilor clienților. "
                "Acesta nu mai este vizibil cumpărătorilor, dar facturile vechi sunt păstrate intacte."
            )
        else:
            # Hard-delete: ștergere fizică din baza de date
            produs.delete()
            messages.success(request, f"Produsul «{nume_produs}» a fost șters definitiv din baza de date.")

        return redirect('catalog:admin_produse_lista')

    # Pasul 4: Afișăm pagina de confirmare cu explicația regulii pentru administrator
    context = {
        'produs': produs,
        'are_comenzi': are_comenzi,
        'titlu': f"Confirmă ștergerea: {produs.nume}",
    }
    return render(request, 'catalog/admin/admin_produs_sterge.html', context)
