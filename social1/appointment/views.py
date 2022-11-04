from math import fabs
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import KorisnikForm, TestForm, FilterForm
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Korisnik, Usluge, Frizer, Termin
import json
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings

@login_required(redirect_field_name='user_login/')
def potvrdi(request):
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
                'pocetak': f'{pocetak.strftime("%H:%M:%S")}',
                'kraj': f'{kraj.strftime("%H:%M:%S")}'
            })

        print(Usluge.objects.get(pk=usluga).duzina.total_seconds())
    except  Exception as e: print(e)

    if request.method == 'POST':
        if 'zakazi_termin' in request.POST:
            params = {
                'user': request.user,
                'usluga': usluga,
                'frizer':frizer,
                'datum':datum,
                'vreme':request.POST['vreme'],
                #'name':request.POST['name'],
                #'broj_telefona':request.POST['broj_telefona'],
                #'uredjaj': request.COOKIES['device']
            }
            data = TestForm(params)
            if data.is_valid():
                data.save()
                messages.success(request,f"Uspešno ste zakazali termin {datum} u {request.POST['vreme']}")
                send_mail("Termin Frizerski salon HASKO",f"<h1>Uspešno ste zakazali termin {datum} u {request.POST['vreme']}</h1>\n",settings.EMAIL_HOST_USER,["muhedin1998@gmail.com",], fail_silently=False)
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
    ls1=usluge[:round(len(usluge)/3)]
    ls2= usluge[round(len(usluge)/3):round(len(usluge)/3+len(usluge)/3)-1]
    ls3= usluge[round(len(usluge)/3+len(usluge)/3)-1:]

    frizeri = Frizer.objects.all()
    interval = 30

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
    if request.user.is_authenticated:
        if request.user.is_superuser:
            frizer = []
            if request.user.username == "hasko123":
                frizer = Frizer.objects.get(name="Hasredin Bećirović")
            if request.user.username == "daris123":
                frizer = Frizer.objects.get(name="Daris Kurtenčsušević")
            if request.user.username == "emil123":
                frizer = Frizer.objects.get(name="Emil Aljković")
            termini = Termin.objects.all().order_by('datum').exclude(datum__lt=datetime.now().date()).filter(frizer=frizer)

        else:
            frizer = Korisnik.objects.get(username = request.user.username)
            termini = Termin.objects.all().order_by('datum').exclude(datum__lt=datetime.now().date()).filter(user=frizer)
    else:
        return redirect(zakazi)
    print(termin)
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
            
            messages.success(request, "Uspesno ste se registrovali")
        else:
            messages.error(request, "Nepravilno popunjena polja, pokusajte ponovo",extra_tags='danger')
    return render(request, 'appointment/account/register.html',{'form':form})

def user_login(request):
    if request.method =="POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        print(user)
        if user is not None:
            print(user)
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

def password_reset_done(request):
    return redirect(zakazi)