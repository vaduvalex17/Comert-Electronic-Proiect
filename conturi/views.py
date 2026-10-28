"""
conturi/views.py

Controllere (views) pentru gestionarea autentificării:
- login_utilizator: autentifică utilizatorul (POST) sau afișează formularul (GET)
- logout_utilizator: deconectează utilizatorul în siguranță (POST obligatoriu)
- inregistrare_utilizator: creează un cont nou de client obișnuit
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from .forms import FormularAutentificare, FormularInregistrare
from .redirectionari import redirectioneaza_sigur


def login_utilizator(request):
    """Gestionează autentificarea utilizatorilor în magazin.

    Dacă utilizatorul este deja logat, este redirecționat pe prima pagină.
    """
    # Pasul 1: Dacă este deja autentificat, nu are sens să vadă formularul de login
    if request.user.is_authenticated:
        return redirect('catalog:acasa')

    # Pasul 2: Procesăm datele trimise prin POST la apăsarea butonului „Conectare”
    if request.method == 'POST':
        formular = FormularAutentificare(data=request.POST)
        if formular.is_valid():
            utilizator = formular.get_user()
            login(request, utilizator)
            messages.success(request, f"Bine ai revenit, {utilizator.username}!")

            # Redirecționăm către pagina cerută anterior (parametrul 'next') sau la Acasă.
            # redirectioneaza_sigur refuză adresele către alte site-uri (protecție „open redirect”).
            return redirectioneaza_sigur(request, request.GET.get('next'), 'catalog:acasa')
        else:
            messages.error(request, "Autentificarea a eșuat. Verifică datele introduse.")
    else:
        # Pasul 3: Afișăm formularul gol pentru cererile obișnuite GET
        formular = FormularAutentificare()

    context = {
        'form': formular,
        'titlu': 'Autentificare',
    }
    return render(request, 'conturi/login.html', context)


def logout_utilizator(request):
    """Deconectează utilizatorul din sesiune.

    Pentru securitate maximă, deconectarea se face prin cerere de tip POST
    pentru a evita atacurile automate prin link-uri GET malițioase.
    """
    # Pasul 1: Verificăm metoda cererii
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Te-ai deconectat cu succes. Te mai așteptăm!")
    else:
        # Dacă totuși cineva încearcă să acceseze prin link direct GET, îl avertizăm și îl trimitem acasă
        messages.warning(request, "Deconectarea se realizează prin butonul dedicat din meniu.")

    # Pasul 2: Redirecționăm pe prima pagină
    return redirect('catalog:acasa')


def inregistrare_utilizator(request):
    """Permite unui vizitator să își creeze un cont nou de client.

    După crearea cu succes a contului, utilizatorul este autentificat automat.
    """
    # Pasul 1: Dacă este deja autentificat, redirecționăm pe prima pagină
    if request.user.is_authenticated:
        return redirect('catalog:acasa')

    # Pasul 2: Procesăm trimiterea formularului prin POST
    if request.method == 'POST':
        formular = FormularInregistrare(request.POST)
        if formular.is_valid():
            # Salvează noul utilizator (rolul va fi implicit de client / non-staff)
            nou_utilizator = formular.save()
            # Autentificare automată imediat după înregistrare
            login(request, nou_utilizator)
            messages.success(request, f"Contul a fost creat cu succes! Bun venit la ElectroMag, {nou_utilizator.first_name}!")
            return redirect('catalog:acasa')
        else:
            messages.error(request, "Formularul conține erori. Te rugăm să verifici câmpurile evidențiate.")
    else:
        # Pasul 3: Formular gol la încărcarea paginii
        formular = FormularInregistrare()

    context = {
        'form': formular,
        'titlu': 'Înregistrare cont nou',
    }
    return render(request, 'conturi/inregistrare.html', context)
