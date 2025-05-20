from math import fabs
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import KorisnikForm, TestForm, FilterForm
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Korisnik, Usluge, Frizer, Termin, Duznik
from django.db.models import Sum
from django.core.serializers import serialize
import json
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.utils.safestring import mark_safe
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver

@receiver(user_logged_in)
def update_ime_prezime(request, user, **kwargs):
    social_info = SocialAccount.objects.filter(user=user).first()
    if social_info:
        extra_data = social_info.extra_data
        # Check if it's Google's data structure
        if 'given_name' in extra_data and 'family_name' in extra_data:
            first_name = extra_data.get('given_name')
            last_name = extra_data.get('family_name')
            full_name = f"{first_name} {last_name}"
        # Check if it's Facebook's data structure
        elif 'name' in extra_data:
            full_name = extra_data.get('name')
        else:
            full_name = None

        if full_name:
            user.ime_prezime = full_name
            user.save()

@login_required
def complete_profile(request):
    if request.method == 'POST':
        broj_telefona = request.POST.get('broj_telefona')
        if broj_telefona:
            request.user.broj_telefona = broj_telefona
            request.user.save()
            return redirect('/')
    return render(request, 'complete_profile.html')

def send_action_email(request, user):
    current_site = get_current_site(request)
    email_sibject = 'Aktivirajte vaš nalog'
    email_body = render_to_string('appointment/account/activate.html',{
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : generate_token().make_token(user)
    })
    email = EmailMessage(subject=email_sibject, body=email_body,from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email.send()

@login_required(redirect_field_name='user_login/')
def potvrdi(request):
    sada = datetime.now()
    viewname = "potvrdi"
    form = TestForm()
    usluga = request.session.get('usluga')
    frizer = request.session.get('frizer')
    datum = request.session.get('datum')
    duration = Usluge.objects.get(pk=usluga).duzina.total_seconds()
    termini = Termin.objects.filter(frizer=frizer,datum=datum)
    termini_2 = []

    try:
        ter = f"{termini[0].vreme}".split(":")

        for ter in termini:
            pocetak = datetime.strptime(f"{ter.datum} {ter.vreme}", '%Y-%m-%d %H:%M:%S')
            kraj = pocetak + ter.usluga.duzina

            termini_2.append({
                "pocetak": f"{pocetak.strftime('%H:%M:%S')}",
                "kraj": f"{kraj.strftime('%H:%M:%S')}"
            })
    except  Exception as e: print(e)

    if request.method == 'POST':
        if 'zakazi_termin' in request.POST:
            name = ""
            broj_telefona = ""
            if request.user.is_superuser:
                name = request.POST['name']
                broj_telefona = request.POST['broj_telefona']
            else:
                name = request.user.ime_prezime
                broj_telefona = request.user.broj_telefona
            params = {
                'user': request.user,
                'usluga': usluga,
                'frizer':frizer,
                'datum':datum,
                'name':name,
                'vreme':request.POST['vreme'],
                'poruka': request.POST['poruka'],
                'godina': sada.year,
                'mesec': format(sada.month, "02d"),
                'dan': format(sada.day, "02d"),                
                'broj_telefona':broj_telefona
            }
            data = TestForm(params)
            if data.is_valid():              
                data.save()
                vreme_za_poruku = datetime.strptime(request.POST['vreme'][:5],"%H:%M")
                za_disp = f"{vreme_za_poruku.hour}:{vreme_za_poruku.minute}"
                messages.success(request,f"Uspešno ste zakazali termin {datum} u {za_disp}")
                return redirect(termin)
            else:
                messages.error(request, "Greska na serveru, pokusajte ponovo", extra_tags='danger')

    context = {
        'filtered_list': json.dumps(list(termini_2)),
        'viewname': viewname,
        'form':form,
        'duration':duration

    }
    return render(request, 'appointment/zakazivanje.html',context)

@login_required(redirect_field_name='user_login/')
def termin(request):
    
    viewname = "termin"
    sada = datetime.now()
    termini = []
    form_filter = TestForm()

    is_next_free = False

    try:
        termin_counter = Termin.objects.filter(user=request.user).count() + 1
    except Exception as e:
        termin_counter = 0
        print("User not logged in")

    is_next_free = "Sledeci termin je besplatan !" if (termin_counter % 15 == 0) else f"Još  {15 - termin_counter % 15} zakazivanja do besplatnog šišanja!"



    print(termin_counter)

    if request.method == 'POST':
        #check if first form button is clicked
        if 'form_filter_button' in request.POST:
            # Sharing parameters between  views
            request.session['frizer'] = request.POST['frizer']
            request.session['datum'] = request.POST['datum']
            request.session['usluga'] = request.POST['usluga']
            # - Sortiranje zauzetih termina -
            return redirect(potvrdi)

    context = {
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'form': form_filter,
        "termin_counter": is_next_free,
    }
    return render(request, 'appointment/zakazivanje.html', context)

def zakazi(request):
    viewname = "zakazi"
    sada = datetime.now()

    usluge = Usluge.objects.all()
    ls1=usluge[:round(len(usluge)/3)-1]
    ls2= usluge[round(len(usluge)/3)-1:round(len(usluge)/3+len(usluge)/3)]
    ls3= usluge[round(len(usluge)/3+len(usluge)/3):]

    frizeri = Frizer.objects.all()
    interval = 30

    if request.method == 'POST':
        if 'kontakt_mail' in request.POST:
            poruka = EmailMessage(subject=request.POST['Subject'], body=f"{request.POST['Name']}\n{request.POST['Email']}\n\n{request.POST['Message']}", from_email=settings.EMAIL_HOST_USER, to=['hasko83@gmail.com'])
            poruka.send()

    context = {
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'usluge': usluge,
        'frizeri': frizeri,
        'ls1':ls1,
        'ls2':ls2,
        "ls3":ls3,
    }
    return render(request, 'appointment/jqr.html', context)

@login_required(redirect_field_name='user_login/')
def zafrizera(request):
    return redirect(opcije_termini)

def user_register(request):
    form = KorisnikForm()

    if request.method =='POST':
        data ={
            'ime_prezime':request.POST['ime_prezime'],
            'username':request.POST['username'],
            'email':request.POST['email'],
            'password':request.POST['password'],
            'password2':request.POST['password2'],
            'broj_telefona':request.POST['broj_telefona'],
        }
        form = KorisnikForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST['password'])
            user.save()
            form.save()

            send_action_email(request, user)
            
            messages.success(request, "Proverite vaše email sanduče za aktivaciju naloga, ukoliko ne vidite email pogledajte u folderu nepoželjno(spam)")
            return redirect(user_login)
        else:
            messages.error(request, "Nepravilno popunjena polja, pokusajte ponovo",extra_tags='danger')
    return render(request, 'appointment/account/register.html',{'form':form})

def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_email_verified:
            return redirect(zakazi)
    if request.method =="POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if not user.is_email_verified:
                send_action_email(request, user)
                messages.error(request, "Email nije aktiviran, proverite poštansko sanduče", extra_tags="danger")
                return redirect(user_login)
            else:
                login(request, user)
            return redirect(zakazi)
        else:
            messages.error(request, "Nepravilno korisnicko ime ili lozinka !", extra_tags="danger")
            return redirect(user_login)

    return render(request, 'appointment/account/login.html')

def otkazivanje(request, termin_id):
    termin = Termin.objects.get(pk=termin_id)
    termin.delete()
    return redirect(zafrizera)

def user_logout(request):

    logout(request)
    return redirect(user_login)

def activate_user(request, uidb64, token):
    
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user = Korisnik.objects.get(pk=uid) 
    except Exception as e:
        user=None
    
    if user and generate_token().check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS, "Email je verifikovan, sada se možete prijaviti")
        return redirect(user_login)
    if request.user.is_authenticated:
        if not request.user.is_email_verified:
            messages.error(request,"Link za prijavu je istekao, prijavite se za novi link", extra_tags="danger")
            return redirect(user_login)
        else:
            return redirect(user_login)
    else:
        messages.error(request,"Morate se prvo prijaviti", extra_tags="danger")
        return redirect(user_login)

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
        return redirect(zakazi)
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
    return redirect(opcije_izvestaj)

def profile_page(request):
    return render(request, 'appointment/profil-page.html')

def notifications_page(request):
    return render(request, 'appointment/notifications_page.html')