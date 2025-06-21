from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from ..forms import TestForm
from datetime import datetime, timedelta
from ..models import Korisnik, Usluge, Frizer, Termin, Duznik
from django.db.models import Sum


def opcije_termini(request):
    frizer = []
    if request.user.username == "hasko123":
        frizer = Frizer.objects.get(name="Hasredin Bećirović")
    if request.user.username == "Muvehid":
        frizer = Frizer.objects.get(name="Muvehid Bećirović")
    if request.user.username == "admin":
        frizer = Frizer.objects.get(name="(bez imena)")

    za_otkazivanje = Usluge.objects.get(pk=15)
    if request.method =='POST':
        form_type = request.POST.get('form_type')
        if form_type == 'form1':
            form = TestForm()
            name = "OTKAZAN DAN"
            broj_telefona = ""
            params = {
                'user': request.user,
                'usluga': za_otkazivanje,
                'frizer':frizer,
                'datum':request.POST['datum'],
                'name':name,
                'poruka': request.POST['poruka'],
                'vreme':'09:00:00',
                'broj_telefona':broj_telefona
                }
            form = TestForm(params)
            if form.is_valid():
                form.save()
        elif form_type == 'form2':
            try:
                user = Korisnik.objects.get(id = request.POST['user_id'])
            except Exception as e:
                print(e)
                user = None
            if user:
                if user.dugovanje is not None:
                    user.dugovanje += int(request.POST['duguje'])
                    user.save()
                    user.refresh_from_db()  # Reload from DB
                else:
                    user.dugovanje = int(request.POST['duguje'])
                    user.save()
                    user.refresh_from_db()  # Reload from DB
            else:
                duznik, created = Duznik.objects.get_or_create(
                name=request.POST['ime_prezime'],
                broj_telefona=request.POST['broj_telefona'],
                defaults={"duguje": request.POST['duguje']}
            )

                if created:
                    print("Sačuvano!")  # New record created
                else:
                    duznik.duguje += int(request.POST['duguje'])  # Convert to int before adding
                    duznik.save()

                    print("Dužnik već postoji! Povećano duguje!")

    if request.user.is_authenticated:
        if request.user.is_superuser:
            termini = Termin.objects.all().order_by('datum','vreme').exclude(datum__lt=datetime.now().date()).filter(frizer=frizer)

        else:
            frizer = Korisnik.objects.get(username = request.user.username)
            termini = Termin.objects.all().order_by('datum').exclude(datum__lt=datetime.now().date()).filter(user=frizer)
    else:
        return redirect('zakazi')
    context = {'termini':termini}

    return render(request, 'appointment/opcije/termini.html', context)


def opcije_klijenti(request):
    user_id = request.GET.get('user_id')

    users = Korisnik.objects.all()
    count = Korisnik.objects.count()

    if (user_id):
        usr = Korisnik.objects.filter(id=user_id).first()
        usr = Korisnik.objects.get(id=usr.id)  # Forces re-fetch
        broj_termina = Termin.objects.filter(user=usr)
        ukupno = 0
        for termin in broj_termina:
            ukupno += termin.cena_termina
        print(ukupno)
        usr.refresh_from_db()
        print(f"SQL Value: {usr.dugovanje} (Type: {type(usr.dugovanje)})")
        print(usr.id)
        print(f"Dugovanje in other view: {usr.dugovanje}")  # Check value
        context = {
            'users': users,
            'count': count,
            'user_view': usr,
            'broj_termina': broj_termina.count(),
            'ukupno': ukupno }
        return render(request, 'appointment/opcije/klijenti.html',context)

    return render(request, 'appointment/opcije/klijenti.html',{'users': users, 'count': count})


def opcije_izvestaj(request):
    today = datetime.now().date()
    duznici = Duznik.objects.all()
    duznici_kor = Korisnik.objects.filter(dugovanje__gt=0)

    periods = {
        '30': today - timedelta(days=30),
        '7': today - timedelta(days=7),
        '1': today - timedelta(days=1),
    }

    earnings_data = {"duznici": duznici,
                     "duznici_kor": duznici_kor}

    for key, start_date in periods.items():
        earnings_per_day = (
            Termin.objects
            .filter(datum__range=[start_date, today])
            .values('datum')
            .annotate(total_earnings=Sum('usluga__cena'))
            .order_by('datum')
        )

        total_earnings = sum(entry['total_earnings'] for entry in earnings_per_day if entry['total_earnings'])

        earnings_data[f'zarada_{key}'] = list(earnings_per_day)
        earnings_data[f'total_{key}'] = total_earnings
        earnings_data[f'sve_{key}'] = earnings_data.get(f'sve_{key}', 0) + total_earnings

    return render(request, 'appointment/opcije/izvestaj.html', earnings_data)


@login_required
def opcije_istorija(request):
    termini_list = Termin.objects.filter(user=request.user)
    paginator = Paginator(termini_list, 50)  # Show 10 images per page

    page_number = request.GET.get('page')
    termini = paginator.get_page(page_number)

    return render(request, 'appointment/opcije/istorija.html', {'termini': termini})


def obrisi_duznika(request, duznik_id):
    try:
        duznik = Duznik.objects.get(pk=duznik_id)
        if duznik.duguje:
            duznik.delete()
        else:
            kor = Korisnik.objects.get(pk=duznik.user.id)
            kor.dugovanje = 0
            kor.save()
            duznik.delete()
    except Duznik.DoesNotExist:
        try:
            kor = Korisnik.objects.get(pk=duznik_id)
            kor.dugovanje = 0
            kor.save()
        except Korisnik.DoesNotExist:
            print(f"No Duznik or Korisnik found with id {duznik_id}")
    except Exception as e:
        print(e)
    return redirect('opcije_izvestaj')