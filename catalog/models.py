"""
catalog/models.py

Modelele bazei de date pentru catalogul comercial:
- Categorie: gruparea produselor (ex: Laptopuri, Telefoane)
- Furnizor: companiile partenere de la care provine marfa
- ModalitateLivrare: metodele de expediere disponibile și costul lor
- Produs: entitatea centrală a magazinului (acoperă cerința R1.3)

Fiecare model include denumiri în limba română (verbose_name), validatori
și metode utilitare explicate pe pași pentru un coleg non-tehnic.
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Categorie(models.Model):
    """Categoria comercială în care sunt încadrate produsele.

    Exemple: Laptopuri, Telefoane, Audio & Căști, Accesorii.
    """

    nume = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nume categorie"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Identificator URL (slug)",
        help_text="Generat automat din nume pentru adrese prietenoase (ex: /categorie/laptopuri/)"
    )
    descriere = models.TextField(
        blank=True,
        verbose_name="Descriere"
    )

    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categorii"
        ordering = ['nume']

    def __str__(self):
        """Returnează numele categoriei pentru afișarea în meniuri și liste."""
        return self.nume

    def save(self, *args, **kwargs):
        """Generează automat slug-ul dacă nu a fost completat manual."""
        if not self.slug:
            self.slug = slugify(self.nume)
        super().save(*args, **kwargs)


class Furnizor(models.Model):
    """Compania parteneră sau distribuitorul care furnizează stocul magazinului."""

    nume = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nume furnizor"
    )
    email = models.EmailField(
        verbose_name="Email contact"
    )
    telefon = models.CharField(
        max_length=20,
        verbose_name="Număr de telefon"
    )

    class Meta:
        verbose_name = "Furnizor"
        verbose_name_plural = "Furnizori"
        ordering = ['nume']

    def __str__(self):
        return self.nume


class ModalitateLivrare(models.Model):
    """Opțiune de livrare disponibilă pentru comenzi (ex: Curier rapid, Ridicare)."""

    nume = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nume modalitate de livrare"
    )
    cost = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Cost livrare (lei)"
    )
    zile_estimate = models.PositiveIntegerField(
        default=2,
        verbose_name="Timp estimat de livrare (zile)"
    )

    class Meta:
        verbose_name = "Modalitate de livrare"
        verbose_name_plural = "Modalități de livrare"
        ordering = ['cost']

    def __str__(self):
        return f"{self.nume} ({self.cost} lei)"


class Produs(models.Model):
    """Modelul central al unui produs din catalog.

    Acoperă toate specificațiile cerute de R1.3:
    - nume, descriere, specificații, preț, stoc, furnizor, modalitate de livrare, categorie.
    """

    nume = models.CharField(
        max_length=200,
        verbose_name="Nume produs"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name="Identificator URL (slug)",
        help_text="Adresă web lizibilă pentru produs (ex: /produs/laptop-gaming-asus/)"
    )
    descriere = models.TextField(
        verbose_name="Descriere produs"
    )
    specificatii = models.TextField(
        blank=True,
        verbose_name="Specificații tehnice",
        help_text="Scrie fiecare specificație pe un rând nou în formatul: Cheie: Valoare (ex: Procesor: Intel i7)"
    )
    pret = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preț (lei)"
    )
    stoc = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stoc disponibil"
    )
    imagine = models.ImageField(
        upload_to='produse/',
        blank=True,
        null=True,
        verbose_name="Fotografie produs"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name='produse',
        verbose_name="Categorie"
    )
    furnizor = models.ForeignKey(
        Furnizor,
        on_delete=models.PROTECT,
        related_name='produse',
        verbose_name="Furnizor"
    )
    modalitati_livrare = models.ManyToManyField(
        ModalitateLivrare,
        related_name='produse',
        verbose_name="Modalități de livrare compatibile"
    )
    activ = models.BooleanField(
        default=True,
        verbose_name="Activ în catalog",
        help_text="Debifează pentru a ascunde produsul fără a-l șterge fizic din comenzile trecute."
    )
    creat_la = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data adăugării"
    )
    actualizat_la = models.DateTimeField(
        auto_now=True,
        verbose_name="Ultima actualizare"
    )

    class Meta:
        verbose_name = "Produs"
        verbose_name_plural = "Produse"
        ordering = ['-creat_la']

    def __str__(self):
        return self.nume

    def save(self, *args, **kwargs):
        """Asigură generarea automată a slug-ului dacă lipsește."""
        if not self.slug:
            slug_de_baza = slugify(self.nume)
            slug_candidat = slug_de_baza
            numar = 1
            # Evităm coliziunile de slug dacă există două produse cu nume identic
            while Produs.objects.filter(slug=slug_candidat).exclude(pk=self.pk).exists():
                slug_candidat = f"{slug_de_baza}-{numar}"
                numar += 1
            self.slug = slug_candidat
        super().save(*args, **kwargs)

    def specificatii_lista(self):
        """Transformă textul specificațiilor într-o listă de perechi (cheie, valoare).

        Exemplu:
        "Ecran: 15.6 inch\nRAM: 16 GB" -> [('Ecran', '15.6 inch'), ('RAM', '16 GB')]
        Această metodă este utilizată direct în template pentru generarea tabelului de specificații.
        """
        perechi = []
        if not self.specificatii:
            return perechi

        for linie in self.specificatii.strip().splitlines():
            linie = linie.strip()
            if not linie:
                continue
            if ':' in linie:
                cheie, valoare = linie.split(':', 1)
                perechi.append((cheie.strip(), valoare.strip()))
            else:
                perechi.append((linie, ''))
        return perechi

    @property
    def imagine_implicita(self):
        """Calea (în static/) a ilustrației afișate când produsul nu are poză încărcată.

        Pentru categoriile demo există câte o ilustrație proprie (static/img/categorii/<slug>.svg);
        pentru orice altă categorie se folosește imaginea generică „Fără imagine”.
        """
        if self.categorie.slug in ('laptopuri', 'telefoane', 'audio', 'periferice'):
            return f"img/categorii/{self.categorie.slug}.svg"
        return "img/produs_implicit.svg"

    @property
    def in_stoc(self):
        """Verifică dacă produsul este disponibil pentru comandă."""
        return self.stoc > 0

    @property
    def stare_stoc(self):
        """Returnează o etichetă lizibilă despre starea stocului pentru clienți."""
        if self.stoc <= 0:
            return "Indisponibil"
        elif self.stoc <= 5:
            return "Stoc limitat"
        return "În stoc"

    @property
    def medie_rating(self):
        """Calculează media stelelor primite (1.0 - 5.0) sau 0 dacă nu are recenzii."""
        from django.db.models import Avg
        agregare = self.recenzii.aggregate(Avg('rating'))['rating__avg']
        if agregare is not None:
            return round(agregare, 1)
        return 0

    @property
    def numar_recenzii(self):
        """Numărul total de recenzii acordate acestui produs."""
        return self.recenzii.count()


class Recenzie(models.Model):
    """Recenzie și notă acordată unui produs de către un cumpărător verificat (Bonus)."""

    produs = models.ForeignKey(
        Produs,
        on_delete=models.CASCADE,
        related_name='recenzii',
        verbose_name="Produs"
    )
    utilizator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recenzii',
        verbose_name="Utilizator"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Notă (1-5 stele)"
    )
    titlu = models.CharField(
        max_length=150,
        verbose_name="Titlu recenzie"
    )
    comentariu = models.TextField(
        verbose_name="Comentariu detaliat"
    )
    creata_la = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data adăugării"
    )

    class Meta:
        verbose_name = "Recenzie"
        verbose_name_plural = "Recenzii"
        unique_together = ('produs', 'utilizator')
        ordering = ['-creata_la']

    def __str__(self):
        return f"{self.rating}★ de {self.utilizator.username} pentru {self.produs.nume}"
