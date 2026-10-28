"""
cumparaturi/forms.py

Formulare pentru procesul de checkout și plasare a comenzii (Cerința R2.2):
- FinalizareComandaForm: colectează datele de livrare, metoda de transport și datele simulate ale cardului.
Include validarea completă a cardului bancar (algoritmul Luhn, data de expirare în viitor și CVV).
"""

from datetime import datetime
import re
from django import forms
from django.core.exceptions import ValidationError
from catalog.models import ModalitateLivrare


class FinalizareComandaForm(forms.Form):
    """Formular pentru finalizarea comenzii (Date livrare + Card bancar simulat)."""

    # -------------------------------------------------------------
    # 1. Date de livrare (Adresă și contact)
    # -------------------------------------------------------------
    nume_destinatar = forms.CharField(
        max_length=150,
        label="Nume complet destinatar",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Ion Popescu'})
    )
    telefon = forms.CharField(
        max_length=20,
        label="Număr de telefon",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 0722 123 456'})
    )
    adresa = forms.CharField(
        max_length=255,
        label="Adresă completă (stradă, număr, bloc, apartament)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Str. Libertății nr. 10, bl. A, ap. 4'})
    )
    oras = forms.CharField(
        max_length=100,
        label="Oraș",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: București'})
    )
    judet = forms.CharField(
        max_length=100,
        label="Județ / Sector",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Sector 1'})
    )
    cod_postal = forms.CharField(
        max_length=20,
        label="Cod poștal",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 010101'})
    )

    modalitate_livrare = forms.ModelChoiceField(
        queryset=ModalitateLivrare.objects.none(),
        label="Modalitate de livrare dorită",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    # -------------------------------------------------------------
    # 2. Date card bancar (Plată simulată)
    # -------------------------------------------------------------
    titular_card = forms.CharField(
        max_length=100,
        label="Nume titular card (așa cum apare pe card)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: ION POPESCU'})
    )
    numar_card = forms.CharField(
        max_length=24,
        label="Număr card bancar (16 cifre)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 4242 4242 4242 4242'})
    )
    expirare_card = forms.CharField(
        max_length=7,
        label="Data expirării (LL/AA)",
        widget=forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '12/28'})
    )
    cvv_card = forms.CharField(
        max_length=4,
        label="Cod de securitate CVV (3 cifre)",
        widget=forms.PasswordInput(attrs={'class': 'form-control text-center', 'placeholder': '123'})
    )

    def __init__(self, livrari_permise=None, *args, **kwargs):
        """Inițializează formularul restrângând modalitățile de livrare la cele comune produselor din coș."""
        super().__init__(*args, **kwargs)
        if livrari_permise is not None:
            self.fields['modalitate_livrare'].queryset = livrari_permise
            if livrari_permise.exists() and not self.initial.get('modalitate_livrare'):
                self.fields['modalitate_livrare'].initial = livrari_permise.first()

    def clean_numar_card(self):
        """Validează numărul cardului folosind algoritmul matematic Luhn."""
        numar = re.sub(r'[\s-]', '', self.cleaned_data.get('numar_card', ''))

        if not numar.isdigit():
            raise ValidationError("Numărul de card trebuie să conțină doar cifre.")

        if len(numar) < 13 or len(numar) > 19:
            raise ValidationError("Numărul de card trebuie să aibă între 13 și 19 cifre (în mod standard 16).")

        # Algoritmul Luhn (checksum utilizat la cardurile Visa, Mastercard etc.)
        suma = 0
        cifre_inversate = numar[::-1]
        for index, caracter in enumerate(cifre_inversate):
            cifra = int(caracter)
            if index % 2 == 1:
                cifra *= 2
                if cifra > 9:
                    cifra -= 9
            suma += cifra

        if suma % 10 != 0:
            raise ValidationError("Numărul de card introdus este invalid (nu trece verificarea algoritmului Luhn).")

        return numar

    def clean_expirare_card(self):
        """Validează formatul LL/AA și faptul că data de expirare este în viitor."""
        text_expirare = self.cleaned_data.get('expirare_card', '').strip()

        # Formatul așteptat este LL/AA (de exemplu 05/27 sau 12/28)
        potrivire = re.match(r'^(0[1-9]|1[0-2])/([0-9]{2})$', text_expirare)
        if not potrivire:
            raise ValidationError("Formatul datei de expirare trebuie să fie LL/AA (ex: 12/28).")

        luna = int(potrivire.group(1))
        an_scurt = int(potrivire.group(2))
        an_complet = 2000 + an_scurt

        acum = datetime.now()
        # Cardul este valid până la sfârșitul lunii respective
        if an_complet < acum.year or (an_complet == acum.year and luna < acum.month):
            raise ValidationError("Cardul bancar este expirat. Introdu un card valabil.")

        return text_expirare

    def clean_cvv_card(self):
        """Validează codul CVV (exact 3 cifre numerice)."""
        cvv = self.cleaned_data.get('cvv_card', '').strip()

        if not cvv.isdigit() or len(cvv) != 3:
            raise ValidationError("Codul CVV trebuie să conțină exact 3 cifre.")

        return cvv
