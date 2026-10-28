"""
cumparaturi/servicii.py

Logica de business centrală pentru plasarea comenzilor (Cerința R2.2).
Această funcție realizează întreaga tranzacție comercială într-un bloc atomic:
- Verifică stocul fiecărui produs cu blocare (select_for_update) împotriva concurenței
- Scade stocul produselor comandate
- Salvează antetul comenzii (Comanda) și snapshot-urile de preț (ArticolComanda)
- Golește coșul utilizatorului

Dacă oricare pas eșuează (ex: stoc insuficient), întreaga tranzacție este anulată
automat (rollback), garantând integritatea bazei de date.
"""

from decimal import Decimal
from django.db import transaction
from catalog.models import Produs
from .models import ArticolComanda, ArticolCos, Comanda


class StocInsuficient(Exception):
    """Excepție aruncată dacă un produs din coș nu mai are stoc suficient în momentul finalizării."""
    pass


def plaseaza_comanda(utilizator, date_livrare, modalitate_livrare, numar_card, cod_reducere_obj=None):
    """Transformă articolele din coșul utilizatorului într-o comandă fermă.

    Parametri:
        utilizator: instanța User a clientului
        date_livrare: dicționar cu câmpurile de adresă (nume_destinatar, telefon, adresa, oras, judet, cod_postal)
        modalitate_livrare: instanța ModalitateLivrare aleasă
        numar_card: numărul cardului validat anterior (se rețin doar ultimele 4 cifre)
        cod_reducere_obj: instanță opțională de CodReducere aplicat din sesiune

    Returnează:
        Instanța Comanda creată cu succes.
    """
    # transaction.atomic garantează „totul sau nimic”: dacă apare o eroare la orice pas,
    # toate modificările din baza de date sunt anulate automat.
    with transaction.atomic():
        # Pasul 1: Preluăm articolele din coșul clientului
        articole_cos = list(
            ArticolCos.objects.filter(utilizator=utilizator).select_related('produs')
        )
        if not articole_cos:
            raise ValueError("Coșul de cumpărături este gol. Nu se poate plasa o comandă fără produse.")

        # Pasul 2: Blocăm rândurile produselor din baza de date (select_for_update)
        # pentru a preveni vânzarea simultană a aceluiași stoc către doi clienți în aceeași secundă.
        produse_ids = [art.produs_id for art in articole_cos]
        produse_blocate = {
            p.id: p for p in Produs.objects.select_for_update().filter(id__in=produse_ids)
        }

        # Pasul 3: Verificăm că există stoc suficient pentru toate produsele din coș
        for art in articole_cos:
            produs_db = produse_blocate.get(art.produs_id)
            if not produs_db or not produs_db.activ:
                raise StocInsuficient(f"Produsul «{art.produs.nume}» nu mai este disponibil pentru vânzare.")

            if produs_db.stoc < art.cantitate:
                raise StocInsuficient(
                    f"Stoc insuficient pentru «{produs_db.nume}». "
                    f"Ai cerut {art.cantitate} buc., dar mai sunt doar {produs_db.stoc} buc. în stoc."
                )

        # Pasul 4: Calculăm sumele finale strict pe server
        subtotal = sum(art.produs.pret * art.cantitate for art in articole_cos)
        valoare_reducere = Decimal('0.00')
        cupon_aplicabil = None

        if cod_reducere_obj:
            este_valid, _ = cod_reducere_obj.este_valid(subtotal)
            if este_valid:
                valoare_reducere = cod_reducere_obj.calculeaza_reducere(subtotal)
                cupon_aplicabil = cod_reducere_obj

        cost_livrare = modalitate_livrare.cost
        total_general = (subtotal - valoare_reducere) + cost_livrare

        # Pasul 5: Extragem doar ultimele 4 cifre ale cardului (securitate conform §6.1)
        card_curatat = numar_card.replace(' ', '').replace('-', '')
        card_ultimele4 = card_curatat[-4:]

        # Pasul 6: Creăm înregistrarea antet a comenzii
        comanda = Comanda.objects.create(
            utilizator=utilizator,
            nume_destinatar=date_livrare['nume_destinatar'],
            telefon=date_livrare['telefon'],
            adresa=date_livrare['adresa'],
            oras=date_livrare['oras'],
            judet=date_livrare['judet'],
            cod_postal=date_livrare['cod_postal'],
            modalitate_livrare=modalitate_livrare,
            cost_livrare=cost_livrare,
            subtotal=subtotal,
            cod_reducere=cupon_aplicabil,
            valoare_reducere=valoare_reducere,
            total=total_general,
            card_ultimele4=card_ultimele4,
            status='plasata',
        )

        # Pasul 7: Salvăm fiecare produs ca snapshot de preț în ArticolComanda și scădem stocul
        for art in articole_cos:
            produs_db = produse_blocate[art.produs_id]

            # Scădem stocul disponibil
            produs_db.stoc -= art.cantitate
            produs_db.save()

            # Creăm snapshot-ul: prețul curent este înghețat pe comanda plasată
            ArticolComanda.objects.create(
                comanda=comanda,
                produs=produs_db,
                nume_produs=produs_db.nume,
                pret_unitar=produs_db.pret,
                cantitate=art.cantitate,
            )

        # Pasul 8: Golim coșul utilizatorului după finalizarea cu succes a achiziției
        ArticolCos.objects.filter(utilizator=utilizator).delete()

        return comanda
