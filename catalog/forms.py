"""
catalog/forms.py

Formulare pentru administrarea catalogului de produse:
- ProdusForm: Formular complet (ModelForm) pentru adăugarea și editarea produselor de către administratori.
Gestionează încărcarea imaginilor, selecția furnizorului, categoriei și metodelor de livrare.
"""

from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from .models import Categorie, Furnizor, ModalitateLivrare, Produs, Recenzie


class ProdusForm(forms.ModelForm):
    """Formular de administrare pentru crearea și editarea produselor (Cerința R1.2)."""

    class Meta:
        model = Produs
        fields = [
            'nume',
            'categorie',
            'furnizor',
            'modalitati_livrare',
            'pret',
            'stoc',
            'descriere',
            'specificatii',
            'imagine',
            'activ',
        ]
        widgets = {
            'nume': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Laptop Gaming ASUS ROG Strix'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select'
            }),
            'furnizor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'modalitati_livrare': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'pret': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'ex: 2999.99'
            }),
            'stoc': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'ex: 10'
            }),
            'descriere': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrie principalele avantaje și caracteristici ale produsului...'
            }),
            'specificatii': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 5,
                'placeholder': "Procesor: Intel Core i7\nMemorie RAM: 16 GB\nStocare: 1 TB SSD"
            }),
            'imagine': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'activ': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_modalitati_livrare(self):
        """Asigură că administratorul selectează cel puțin o modalitate de livrare."""
        modalitati = self.cleaned_data.get('modalitati_livrare')
        if not modalitati or modalitati.count() == 0:
            raise ValidationError("Trebuie să bifezi cel puțin o modalitate de livrare compatibilă cu acest produs.")
        return modalitati

    def clean_pret(self):
        """Validează că prețul este strict pozitiv."""
        pret = self.cleaned_data.get('pret')
        if pret is not None and pret <= Decimal('0.00'):
            raise ValidationError("Prețul produsului trebuie să fie mai mare de 0 lei.")
        return pret

    def clean_stoc(self):
        """Validează că stocul este cel puțin 0."""
        stoc = self.cleaned_data.get('stoc')
        if stoc is not None and stoc < 0:
            raise ValidationError("Stocul nu poate fi un număr negativ.")
        return stoc


class RecenzieForm(forms.ModelForm):
    """Formular pentru lăsarea unei recenzii și note de către cumpărătorii verificați (Bonus)."""

    RATING_OPTIUNI = [
        (5, '★★★★★ (5 stele - Excelent)'),
        (4, '★★★★☆ (4 stele - Foarte bun)'),
        (3, '★★★☆☆ (3 stele - Mediu)'),
        (2, '★★☆☆☆ (2 stele - Nemulțumitor)'),
        (1, '★☆☆☆☆ (1 stea - Slab)'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_OPTIUNI,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Notă acordată"
    )

    class Meta:
        model = Recenzie
        fields = ['rating', 'titlu', 'comentariu']
        widgets = {
            'titlu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Recomand cu căldură, performanță impecabilă!'
            }),
            'comentariu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Împărtășește experiența ta cu acest produs (calitate, livrare, fiabilitate)...'
            }),
        }
