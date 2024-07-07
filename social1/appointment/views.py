from math import fabs
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import KorisnikForm, TestForm, FilterForm
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Korisnik, Usluge, Frizer, Termin
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

            # usl = Usluge.objects.get(pk=request.POST['usluga'])
            # zauzet = datetime(termini[0].datum,termini[0].vreme)
            # Ovo radi ! vr + usl.duzina
            # duration = timedelta(usl.duzina)
            termini_2.append({
                "pocetak": f"{pocetak.strftime('%H:%M:%S')}",
                "kraj": f"{kraj.strftime('%H:%M:%S')}"
            })

        print(Usluge.objects.get(pk=usluga).duzina.total_seconds())
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
                'godina': sada.year,
                'mesec': format(sada.month, "02d"),
                'dan': format(sada.day, "02d"),                
                'broj_telefona':broj_telefona
                #'name':request.POST['name'],
                #'uredjaj': request.COOKIES['device']
            }
            data = TestForm(params)
            if data.is_valid():              
                data.save()
                vreme_za_poruku = datetime.strptime(request.POST['vreme'][:5],"%H:%M")
                za_disp = f"{vreme_za_poruku.hour}:{vreme_za_poruku.minute}"
                messages.success(request,f"Uspešno ste zakazali termin {datum} u {za_disp}")
                print("Form was VALID AND PASSED")
                return redirect(termin)

                # print(data)
            else:
                messages.error(request, "Greska na serveru, pokusajte ponovo", extra_tags='danger')
                print(f"From WAS NOT VALID ! -")
                # print(data)

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

    if request.method == 'POST':
        #check if first form button is clicked
        if 'form_filter_button' in request.POST:

            # termini = Termin.objects.filter(usluga=request.POST['usluga'], frizer=request.POST['frizer'], datum=request.POST['datum'])
            # request.session['termini'] = Termin.objects.filter( frizer=request.POST['frizer'], datum=request.POST['datum'])
            # Sharing parameters between  views
            request.session['frizer'] = request.POST['frizer']
            request.session['datum'] = request.POST['datum']
            request.session['usluga'] = request.POST['usluga']
            # - Sortiranje zauzetih termina -
            return redirect(potvrdi)

    context = {
        #'filter_form': form_filter,

        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'form': form_filter
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
    frizer = []
    if request.user.username == "hasko123":
        frizer = Frizer.objects.get(name="Hasredin Bećirović")
    if request.user.username == "daris123":
        frizer = Frizer.objects.get(name="Muvehid Bećirović")
    if request.user.username == "emil123":
        frizer = Frizer.objects.get(name="Emil Aljković")

    za_otkazivanje = Usluge.objects.get(pk=15)
    print(za_otkazivanje.name)
    if request.method =='POST':
        form = TestForm()
        name = "OTKAZAN DAN"
        broj_telefona = ""
        params = {
            'user': request.user,
            'usluga': za_otkazivanje,
            'frizer':frizer,
            'datum':request.POST['datum'],
            'name':name,
            'vreme':'09:00:00',
            # 'godina': sada.year,
            # 'mesec': format(sada.month, "02d"),
            # 'dan': format(sada.day, "02d"),                
            'broj_telefona':broj_telefona
            #'name':request.POST['name'],
            #'uredjaj': request.COOKIES['device']
            }
        form = TestForm(params)
        if form.is_valid():
            form.save()
        print(request.POST['datum'])
    if request.user.is_authenticated:
        if request.user.is_superuser:
            termini = Termin.objects.all().order_by('datum','vreme').exclude(datum__lt=datetime.now().date()).filter(frizer=frizer)

        else:
            frizer = Korisnik.objects.get(username = request.user.username)
            termini = Termin.objects.all().order_by('datum').exclude(datum__lt=datetime.now().date()).filter(user=frizer)
    else:
        return redirect(zakazi)
    context = {'termini':termini}
    return render(request, 'appointment/zafrizera.html', context)


# def user_register(request):
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             redirect(zakazi)

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
        print(user)
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
            #return render(request,'appointment/account/authentication-failed.html',{'user': user})
            messages.error(request,"Link za prijavu je istekao, prijavite se za novi link", extra_tags="danger")
            return redirect(user_login)
        else:
            return redirect(user_login)
    else:
        messages.error(request,"Morate se prvo prijaviti", extra_tags="danger")
        return redirect(user_login)
