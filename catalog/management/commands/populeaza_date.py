"""
catalog/management/commands/populeaza_date.py

Comandă de management personalizată pentru încărcarea datelor inițiale demonstrative:
- Cont de administrator (admin / admin123)
- Cont de client obișnuit (client / client123)
- 4 categorii comerciale
- 3 furnizori parteneri
- 3 modalități de livrare
- 20 de produse cu specificații detaliate și realiste

Comanda este IDEMPOTENTĂ: poate fi rulată de oricâte ori fără a crea dubluri.
Rulare:
    python manage.py populeaza_date
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from catalog.models import Categorie, Furnizor, ModalitateLivrare, Produs

User = get_user_model()


class Command(BaseCommand):
    help = "Populează baza de date cu date demonstrative pentru testare și prezentare."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Încep popularea bazei de date cu date demo..."))

        # -------------------------------------------------------------
        # Pasul 1: Creare conturi demonstrative (admin și client)
        # -------------------------------------------------------------
        admin_user, creat_admin = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@electromag.ro',
                'first_name': 'Administrator',
                'last_name': 'Sistem',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if creat_admin:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Cont administrator creat: admin / admin123"))
        else:
            self.stdout.write("  Contul admin există deja.")

        client_user, creat_client = User.objects.get_or_create(
            username='client',
            defaults={
                'email': 'client@exemplu.ro',
                'first_name': 'Ion',
                'last_name': 'Popescu',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if creat_client:
            client_user.set_password('client123')
            client_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Cont client creat: client / client123"))
        else:
            self.stdout.write("  Contul client există deja.")

        # -------------------------------------------------------------
        # Pasul 2: Categorii
        # -------------------------------------------------------------
        categorii_date = [
            ("Laptopuri & Calculatoare", "laptopuri", "Laptopuri de gaming, ultrabook-uri business și sisteme PC performante."),
            ("Telefoane & Tablete", "telefoane", "Cele mai noi smartphone-uri, tablete și accesorii inteligente."),
            ("Audio & Căști", "audio", "Căști wireless, boxe portabile și sisteme audio de înaltă fidelitate."),
            ("Periferice & Accesorii", "periferice", "Tastaturi mecanice, mouși de precizie, monitoare și cabluri."),
        ]
        categorii = {}
        for nume, slug, descriere in categorii_date:
            cat, _ = Categorie.objects.get_or_create(
                slug=slug,
                defaults={'nume': nume, 'descriere': descriere}
            )
            categorii[slug] = cat
        self.stdout.write(self.style.SUCCESS(f"✓ {len(categorii)} categorii verificate/create."))

        # -------------------------------------------------------------
        # Pasul 3: Furnizori
        # -------------------------------------------------------------
        furnizori_date = [
            ("TechDistrib România SRL", "comenzi@techdistrib.ro", "0721.111.222"),
            ("ElectroPro Import SRL", "contact@electropro.ro", "0732.333.444"),
            ("DigitalWorld Logistics SRL", "suport@digitalworld.ro", "0743.555.666"),
        ]
        furnizori = []
        for nume, email, tel in furnizori_date:
            f, _ = Furnizor.objects.get_or_create(
                nume=nume,
                defaults={'email': email, 'telefon': tel}
            )
            furnizori.append(f)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(furnizori)} furnizori verificați/creați."))

        # -------------------------------------------------------------
        # Pasul 4: Modalități de Livrare
        # -------------------------------------------------------------
        livrari_date = [
            ("Curier Rapid (Livrare la ușă)", Decimal("19.99"), 1),
            ("Livrare în Easybox", Decimal("11.99"), 2),
            ("Ridicare gratuită din showroom", Decimal("0.00"), 1),
        ]
        modalitati_livrare = []
        for nume, cost, zile in livrari_date:
            m, _ = ModalitateLivrare.objects.get_or_create(
                nume=nume,
                defaults={'cost': cost, 'zile_estimate': zile}
            )
            modalitati_livrare.append(m)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(modalitati_livrare)} modalități de livrare verificate/create."))

        # -------------------------------------------------------------
        # Pasul 5: Produse (20 de produse detaliate)
        # -------------------------------------------------------------
        produse_date = [
            # Categoria: Laptopuri (5 produse)
            {
                "nume": "Laptop Gaming ASUS ROG Strix G16",
                "slug": "laptop-gaming-asus-rog-strix-g16",
                "categorie": categorii["laptopuri"],
                "furnizor": furnizori[0],
                "pret": Decimal("7499.99"),
                "stoc": 8,
                "descriere": "Performanță extremă pentru pasionații de gaming și creatori de conținut. Ecran IPS rapid de 165Hz și sistem avansat de răcire cu metal lichid.",
                "specificatii": "Procesor: Intel Core i7-13650HX\nPlacă video: NVIDIA GeForce RTX 4060 8GB\nMemorie RAM: 16 GB DDR5\nStocare: 1 TB SSD NVMe\nEcran: 16 inch QHD+ 165Hz\nSistem de operare: Fără sistem (FreeDOS)\nGreutate: 2.5 kg",
            },
            {
                "nume": "Laptop Apple MacBook Air 13 M3",
                "slug": "laptop-apple-macbook-air-13-m3",
                "categorie": categorii["laptopuri"],
                "furnizor": furnizori[1],
                "pret": Decimal("6299.00"),
                "stoc": 12,
                "descriere": "Uimitor de subțire și incredibil de rapid. Autonomie de până la 18 ore, ecran Liquid Retina superb și construcție durabilă din aluminiu reciclat.",
                "specificatii": "Procesor: Apple M3 (8 nuclee CPU, 8 nuclee GPU)\nMemorie unificată: 16 GB\nStocare: 512 GB SSD\nEcran: 13.6 inch Liquid Retina (2560x1664)\nAutonomie: Până la 18 ore\nGreutate: 1.24 kg\nCuloare: Midnight",
            },
            {
                "nume": "Ultrabook Lenovo ThinkPad T14 Gen 4",
                "slug": "ultrabook-lenovo-thinkpad-t14-gen-4",
                "categorie": categorii["laptopuri"],
                "furnizor": furnizori[2],
                "pret": Decimal("5499.50"),
                "stoc": 5,
                "descriere": "Standardul de aur pentru mediul corporate. Tastatură legendară ergonomică, securitate ThinkShield și fiabilitate testată conform standardelor militare.",
                "specificatii": "Procesor: AMD Ryzen 7 PRO 7840U\nMemorie RAM: 32 GB LPDDR5x\nStocare: 1 TB SSD PCIe 4.0\nEcran: 14 inch WUXGA IPS antireflex\nSecuritate: Senzor amprentă, cameră IR cu obturator\nSistem operare: Windows 11 Pro",
            },
            {
                "nume": "Laptop HP Pavilion 15 Business",
                "slug": "laptop-hp-pavilion-15-business",
                "categorie": categorii["laptopuri"],
                "furnizor": furnizori[0],
                "pret": Decimal("2899.99"),
                "stoc": 15,
                "descriere": "Laptop versatil pentru birou, școală și activități cotidiene. Difuzoare reglate de B&O și încărcare rapidă HP Fast Charge.",
                "specificatii": "Procesor: Intel Core i5-1235U\nMemorie RAM: 16 GB DDR4\nStocare: 512 GB SSD M.2\nEcran: 15.6 inch Full HD IPS\nConectivitate: Wi-Fi 6, Bluetooth 5.3, USB-C\nGreutate: 1.74 kg",
            },
            {
                "nume": "Laptop Dell XPS 15 9530",
                "slug": "laptop-dell-xps-15-9530",
                "categorie": categorii["laptopuri"],
                "furnizor": furnizori[1],
                "pret": Decimal("9899.00"),
                "stoc": 2,  # Stoc limitat
                "descriere": "Putere colosală într-un șasiu impecabil din aluminiu prelucrat CNC și fibră de carbon. Ecran OLED tactil 3.5K cu o reproducere fidelă a culorilor.",
                "specificatii": "Procesor: Intel Core i9-13900H\nPlacă video: NVIDIA RTX 4070 8GB GDDR6\nMemorie RAM: 32 GB DDR5\nStocare: 1 TB SSD PCIe 4.0\nEcran: 15.6 inch OLED 3.5K Touch\nGreutate: 1.92 kg",
            },

            # Categoria: Telefoane (5 produse)
            {
                "nume": "Smartphone Apple iPhone 15 Pro",
                "slug": "smartphone-apple-iphone-15-pro",
                "categorie": categorii["telefoane"],
                "furnizor": furnizori[1],
                "pret": Decimal("5799.00"),
                "stoc": 10,
                "descriere": "Forjat din titan de calitate aerospațială. Cip revoluționar A17 Pro, buton Acțiune personalizabil și sistem avansat de camere de 48 MP.",
                "specificatii": "Cip: A17 Pro cu GPU cu 6 nuclee\nStocare: 256 GB\nEcran: 6.1 inch Super Retina XDR ProMotion 120Hz\nCameră: Triplă 48MP + 12MP Ultra-wide + 12MP Telephoto 3x\nConector: USB-C 3.0\nRezistență: IP68 la apă și praf",
            },
            {
                "nume": "Smartphone Samsung Galaxy S24 Ultra",
                "slug": "smartphone-samsung-galaxy-s24-ultra",
                "categorie": categorii["telefoane"],
                "furnizor": furnizori[0],
                "pret": Decimal("6199.99"),
                "stoc": 7,
                "descriere": "Epoca Galaxy AI este aici. Șasiu din titan, stylus S-Pen integrat și cameră incredibilă de 200 MP cu zoom optic spațial.",
                "specificatii": "Procesor: Snapdragon 8 Gen 3 for Galaxy\nMemorie RAM: 12 GB\nStocare: 512 GB\nEcran: 6.8 inch Dynamic AMOLED 2X, 2600 nits\nCameră principală: 200 MP cu stabilizare OIS\nBaterie: 5000 mAh cu încărcare 45W",
            },
            {
                "nume": "Smartphone Google Pixel 8",
                "slug": "smartphone-google-pixel-8",
                "categorie": categorii["telefoane"],
                "furnizor": furnizori[2],
                "pret": Decimal("3499.00"),
                "stoc": 14,
                "descriere": "Cel mai inteligent telefon Google, propulsat de procesorul Tensor G3. Fotografie computațională de top și 7 ani de actualizări Android garantate.",
                "specificatii": "Procesor: Google Tensor G3 cu cip de securitate Titan M2\nMemorie RAM: 8 GB\nStocare: 128 GB\nEcran: 6.2 inch Actua OLED 120Hz\nCamere: Principală 50MP Octa PD + 12MP ultrawide\nAutonomie: Peste 24 de ore",
            },
            {
                "nume": "Tabletă Apple iPad Air 11 M2",
                "slug": "tableta-apple-ipad-air-11-m2",
                "categorie": categorii["telefoane"],
                "furnizor": furnizori[1],
                "pret": Decimal("3699.00"),
                "stoc": 9,
                "descriere": "Puterea cipului M2 acum pe noul iPad Air. Compatibil cu Apple Pencil Pro și tastatura Magic Keyboard, ideal pentru schițe și productivitate.",
                "specificatii": "Cip: Apple M2 (8 nuclee CPU, 10 nuclee GPU)\nStocare: 128 GB\nEcran: 11 inch Liquid Retina cu True Tone\nCameră: 12 MP Wide pe spate, 12 MP Ultra Wide frontală\nConectivitate: Wi-Fi 6E, Bluetooth 5.3",
            },
            {
                "nume": "Smartphone Xiaomi Redmi Note 13 Pro+",
                "slug": "smartphone-xiaomi-redmi-note-13-pro-plus",
                "categorie": categorii["telefoane"],
                "furnizor": furnizori[0],
                "pret": Decimal("1899.99"),
                "stoc": 0,  # Produs indisponibil pentru testare stoc 0
                "descriere": "Campionul raportului calitate-preț. Cameră de 200 MP, ecran curbat CrystalRes AMOLED de 1.5K și încărcare ultra-rapidă de 120W (0-100% în 19 minute).",
                "specificatii": "Procesor: MediaTek Dimensity 7200 Ultra\nMemorie RAM: 12 GB\nStocare: 512 GB\nEcran: 6.67 inch AMOLED 120Hz curbat\nÎncărcare: 120W HyperCharge cu încărcător inclus\nProtecție: IP68",
            },

            # Categoria: Audio (5 produse)
            {
                "nume": "Căști Over-Ear Sony WH-1000XM5",
                "slug": "casti-over-ear-sony-wh-1000xm5",
                "categorie": categorii["audio"],
                "furnizor": furnizori[0],
                "pret": Decimal("1599.00"),
                "stoc": 18,
                "descriere": "Lider în anularea activă a zgomotului de fond (ANC). Două procesoare audio și opt microfoane oferă o claritate desăvârșită la apeluri și audiție.",
                "specificatii": "Tip căști: Over-Ear Wireless\nAutonomie: 30 de ore cu ANC pornit, 40 fără ANC\nTehnologie ANC: Procesor integrat V1 + procesor QN1\nCodecuri: LDAC, AAC, SBC\nGreutate: 250 grame\nConexiune: Bluetooth 5.2 multipunct",
            },
            {
                "nume": "Căști True Wireless Apple AirPods Pro 2 (USB-C)",
                "slug": "casti-apple-airpods-pro-2-usb-c",
                "categorie": categorii["audio"],
                "furnizor": furnizori[1],
                "pret": Decimal("1249.00"),
                "stoc": 25,
                "descriere": "Anulare activă a zgomotului de până la 2x mai eficientă. Audio Spațial personalizat cu urmărire dinamică a mișcărilor capului și carcasă MagSafe.",
                "specificatii": "Cip: Apple H2 în căști, cip U1 în carcasă\nConectivitate: Bluetooth 5.3\nAutonomie: Până la 6 ore ascultare (30 ore cu carcasa)\nPort încărcare: USB-C și MagSafe wireless\nRezistență: IP54 la praf, transpirație și apă",
            },
            {
                "nume": "Boxă Portabilă JBL Charge 5",
                "slug": "boxa-portabila-jbl-charge-5",
                "categorie": categorii["audio"],
                "furnizor": furnizori[2],
                "pret": Decimal("749.90"),
                "stoc": 11,
                "descriere": "Sunet puternic original JBL Pro Sound cu difuzor de bas dedicat. Funcționează și ca baterie externă pentru a-ți încărca telefonul la petreceri.",
                "specificatii": "Putere ieșire: 40W RMS (30W woofer + 10W tweeter)\nAutonomie baterie: Până la 20 de ore\nCapacitate baterie: 7500 mAh\nRezistență: IP67 complet rezistent la apă și praf\nFuncție PartyBoost: Permite legarea mai multor boxe",
            },
            {
                "nume": "Soundbar Samsung HW-Q990D 11.1.4",
                "slug": "soundbar-samsung-hw-q990d-11-1-4",
                "categorie": categorii["audio"],
                "furnizor": furnizori[0],
                "pret": Decimal("4499.00"),
                "stoc": 3,  # Stoc limitat
                "descriere": "Experiență de cinematograf chiar în livingul tău. Sunet surround 3D imersiv Wireless Dolby Atmos cu subwoofer masiv și sateliți spate incluși.",
                "specificatii": "Canale audio: 11 canale frontale și surround, 1 canal subwoofer, 4 difuzoare up-firing\nPutere totală: 656W\nFormate suportate: Dolby Atmos, DTS:X, Q-Symphony\nConexiuni: HDMI eARC, Wi-Fi, Bluetooth, Optical",
            },
            {
                "nume": "Căști Gaming HyperX Cloud III Wireless",
                "slug": "casti-gaming-hyperx-cloud-iii-wireless",
                "categorie": categorii["audio"],
                "furnizor": furnizori[2],
                "pret": Decimal("699.00"),
                "stoc": 20,
                "descriere": "Evoluția unei legende printre gamerii profesioniști. Confort inegalabil datorită spumei cu memorie HyperX și autonomie uriașă de până la 120 de ore.",
                "specificatii": "Conectivitate: Wireless 2.4GHz prin dongle USB-C/USB-A\nAutonomie: Până la 120 de ore de joc\nDifuzoare: 53 mm cu magneți din neodim\nMicrofon: Detașabil de 10 mm cu filtru anti-pop intern\nCompatibilitate: PC, PS5, PS4, Nintendo Switch",
            },

            # Categoria: Periferice & Accesorii (5 produse)
            {
                "nume": "Mouse Wireless Logitech MX Master 3S",
                "slug": "mouse-wireless-logitech-mx-master-3s",
                "categorie": categorii["periferice"],
                "furnizor": furnizori[0],
                "pret": Decimal("499.99"),
                "stoc": 30,
                "descriere": "Iconul productivității remasterizat. Clicuri silențioase Quiet Clicks și senzor optic de 8000 DPI capabil să funcționeze chiar și pe suprafețe de sticlă.",
                "specificatii": "Senzor: Darkfield de înaltă precizie (200 - 8000 DPI)\nScroll: Rotiță electromagnetică MagSpeed (1000 linii/secundă)\nConectivitate: Bluetooth Low Energy + receptor Logi Bolt\nAutonomie: Până la 70 de zile cu o încărcare completă\nCompatibilitate: Windows, macOS, Linux, iPadOS",
            },
            {
                "nume": "Tastatură Mecanică Keychron K2 Pro QMK/VIA",
                "slug": "tastatura-mecanica-keychron-k2-pro",
                "categorie": categorii["periferice"],
                "furnizor": furnizori[2],
                "pret": Decimal("579.00"),
                "stoc": 12,
                "descriere": "Tastatură mecanică fără fir personalizabilă 75%. Switch-uri lubrifiate din fabrică, taste PBT dublu strat și suport complet pentru programarea tastelor QMK/VIA.",
                "specificatii": "Format: 75% compact (84 taste)\nSwitch-uri: Keychron K Pro Red (liniare, silențioase, hot-swappable)\nIluminare: RGB cu 22 de efecte dinamice\nConectivitate: Bluetooth 5.1 (până la 3 dispozitive) și cablu USB-C\nBaterie: 4000 mAh",
            },
            {
                "nume": "Monitor Gaming LG UltraGear 27GP850P-B",
                "slug": "monitor-gaming-lg-ultragear-27gp850p-b",
                "categorie": categorii["periferice"],
                "furnizor": furnizori[0],
                "pret": Decimal("1449.00"),
                "stoc": 6,
                "descriere": "Claritate și fluiditate desăvârșită. Panou Nano IPS de 1ms, rată de refresh overclockabilă la 180Hz și compatibilitate certificată NVIDIA G-Sync.",
                "specificatii": "Diagonală: 27 inch (68.5 cm)\nRezoluție: QHD 2560 x 1440 pixeli\nPanou: Nano IPS cu 98% acoperire DCI-P3\nTimp de răspuns: 1ms GtG\nRată de reîmprospătare: 165Hz (OC 180Hz)\nTehnologii: G-Sync Compatible, AMD FreeSync Premium, HDR400",
            },
            {
                "nume": "Cameră Web Logitech MX Brio 4K UHD",
                "slug": "camera-web-logitech-mx-brio-4k-uhd",
                "categorie": categorii["periferice"],
                "furnizor": furnizori[1],
                "pret": Decimal("1099.00"),
                "stoc": 4,  # Stoc limitat
                "descriere": "Webcam premium pentru streaming și ședințe de afaceri. Senzor avansat Ultra HD 4K cu pixeli mari, reducere a zgomotului video cu AI și mod Show Mode.",
                "specificatii": "Rezoluție maximă: 4K UHD la 30 fps sau 1080p la 60 fps\nCâmp vizual (FOV): Reglabil la 65°, 78° sau 90°\nMicrofoane: Microfoane duble cu filtrare zgomot de fond\nConexiune: Cablu detașabil USB-C la USB-C\nObturator fizic: Intimitate garantată prin rotiță mecanică",
            },
            {
                "nume": "Hub USB-C Anker 8-în-1 PowerExpand",
                "slug": "hub-usb-c-anker-8-in-1-powerexpand",
                "categorie": categorii["periferice"],
                "furnizor": furnizori[2],
                "pret": Decimal("299.90"),
                "stoc": 16,
                "descriere": "Extinde porturile laptopului tău printr-o singură conexiune USB-C. Permite încărcare Pass-Through de până la 100W, ieșire video HDMI 4K și cititor SD.",
                "specificatii": "Porturi: 1x HDMI 4K@60Hz, 1x USB-C PD 100W, 2x USB-A 3.1 (10Gbps), 1x USB-C date, 1x Gigabit Ethernet, 1x slot SD, 1x slot microSD\nMaterial: Carcasă din aliaj de aluminiu pentru disipare căldură\nCompatibilitate: MacBook, Dell XPS, ThinkPad, iPad Pro",
            },
        ]

        total_create = 0
        for date_p in produse_date:
            prod, creat = Produs.objects.get_or_create(
                slug=date_p["slug"],
                defaults={
                    "nume": date_p["nume"],
                    "categorie": date_p["categorie"],
                    "furnizor": date_p["furnizor"],
                    "pret": date_p["pret"],
                    "stoc": date_p["stoc"],
                    "descriere": date_p["descriere"],
                    "specificatii": date_p["specificatii"],
                    "activ": True,
                }
            )
            # Asociem toate modalitățile de livrare
            prod.modalitati_livrare.set(modalitati_livrare)
            if creat:
                total_create += 1

        self.stdout.write(self.style.SUCCESS(f"✓ {len(produse_date)} produse verificate (din care {total_create} nou-create)."))
        self.stdout.write(self.style.SUCCESS("Baza de date a fost populată cu succes!"))
