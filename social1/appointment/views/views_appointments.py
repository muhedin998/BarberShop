from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import TestForm
from django.contrib import messages
from datetime import datetime
from ..models import Usluge, Frizer, Termin, Notification
from django.core.serializers import serialize
import json
from django.core.mail import EmailMessage
from django.conf import settings


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
                Notification.objects.create(
                    user=request.user,
                    title="Novi termin",
                    message=f"Uspešno ste zakazali termin {datum} u {za_disp} sa frizerom {Frizer.objects.get(pk=frizer).name} za uslugu {Usluge.objects.get(pk=usluga).name}.",
                )
                return redirect('termin')
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


def otkazivanje(request, termin_id):
    termin = Termin.objects.get(pk=termin_id)
    termin.delete()
    return redirect('zafrizera')


@login_required(redirect_field_name='user_login/')
def zafrizera(request):
    return redirect('opcije_termini')