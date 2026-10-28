"""
conturi/forms.py

Formulare pentru autentificare și înregistrare utilizatori:
- FormularInregistrare: permite crearea unui cont nou de client obișnuit
- FormularAutentificare: verifică numele de utilizator și parola la conectare

Toate câmpurile folosesc clase Bootstrap (form-control) pentru o interfață modernă.
"""

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class FormularInregistrare(UserCreationForm):
    """Formular pentru crearea unui cont de client.

    Adaugă obligativitatea adresei de email și a numelui/prenumelui,
    asigurându-se că utilizatorul creat are rol de client obișnuit (non-staff).
    """

    email = forms.EmailField(
        required=True,
        label="Adresă de email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplu@email.ro'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        label="Prenume",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Ion'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        label="Nume de familie",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Popescu'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicăm clase Bootstrap 5 pe toate câmpurile formularului
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Alege un nume de utilizator'})
        self.fields['username'].label = "Nume de utilizator"
        self.fields['username'].help_text = "Maxim 150 de caractere. Litere, cifre și caracterele @/./+/-/_."
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parolă sigură'})
            self.fields['password1'].label = "Parolă"
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmă parola'})
            self.fields['password2'].label = "Confirmare parolă"

    def clean_email(self):
        """Verifică unicitatea adresei de email în sistem."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("O adresă de email identică este deja asociată unui cont.")
        return email

    def save(self, commit=True):
        """Salvează noul utilizator garantând că rolul este doar de client (non-staff)."""
        utilizator = super().save(commit=False)
        utilizator.email = self.cleaned_data['email']
        utilizator.first_name = self.cleaned_data['first_name']
        utilizator.last_name = self.cleaned_data['last_name']
        utilizator.is_staff = False
        utilizator.is_superuser = False
        if commit:
            utilizator.save()
        return utilizator


class FormularAutentificare(forms.Form):
    """Formular simplu și sigur pentru conectarea în aplicație."""

    username = forms.CharField(
        label="Nume de utilizator",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introdu utilizatorul', 'autofocus': True})
    )
    password = forms.CharField(
        label="Parolă",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Introdu parola'})
    )

    def clean(self):
        """Validează credențialele prin funcția de autentificare Django."""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            utilizator = authenticate(username=username, password=password)
            if utilizator is None:
                raise ValidationError("Numele de utilizator sau parola sunt incorecte.")
            if not utilizator.is_active:
                raise ValidationError("Acest cont de utilizator a fost dezactivat.")
            self.utilizator = utilizator

        return cleaned_data

    def get_user(self):
        """Returnează utilizatorul autentificat."""
        return getattr(self, 'utilizator', None)
