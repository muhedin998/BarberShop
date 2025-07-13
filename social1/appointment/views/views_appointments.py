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
from django.template.loader import render_to_string
from django.utils import timezone


@login_required(redirect_field_name='user_login/')
def potvrdi(request):
    sada = datetime.now()
    viewname = "potvrdi"
    form = TestForm()
    usluga = request.session.get('usluga')
    frizer = request.session.get('frizer')
    datum = request.session.get('datum')
    dodatne_usluge = request.session.get('dodatne_usluge', [])
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
            # Validate booking date is within 30 days
            try:
                booking_date = datetime.strptime(datum, '%Y-%m-%d').date()
                today = sada.date()
                max_booking_date = today + timezone.timedelta(days=30)
                
                if booking_date < today:
                    messages.error(request, "Ne možete zakazati termin u prošlosti", extra_tags='danger')
                    return redirect('potvrdi')
                elif booking_date > max_booking_date:
                    messages.error(request, "Možete zakazati termin maksimalno 30 dana unapred", extra_tags='danger')
                    return redirect('potvrdi')
            except ValueError:
                messages.error(request, "Neispravno unet datum", extra_tags='danger')
                return redirect('potvrdi')
            
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
                'broj_telefona':broj_telefona,
                'dodatne_usluge': dodatne_usluge
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

    # Pripremi podatke o dodatnim uslugama za prikaz
    dodatne_usluge_nazivi = []
    if dodatne_usluge:
        dodatne_usluge_objekti = Usluge.objects.filter(id__in=dodatne_usluge)
        dodatne_usluge_nazivi = [usluga.name for usluga in dodatne_usluge_objekti]

    context = {
        'filtered_list': json.dumps(list(termini_2)),
        'viewname': viewname,
        'form':form,
        'duration':duration,
        'dodatne_usluge_nazivi': dodatne_usluge_nazivi

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
            
            # Prikupi dodatne usluge
            dodatne_usluge = []
            for key, value in request.POST.items():
                if key.startswith('dodatna_usluga_') and value:
                    dodatne_usluge.append(int(value))
            
            # Ograniči na maksimalno 3 dodatne usluge
            if len(dodatne_usluge) > 3:
                dodatne_usluge = dodatne_usluge[:3]
                
            request.session['dodatne_usluge'] = dodatne_usluge
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
            # Render professional email template
            email_body = render_to_string('appointment/emails/contact_email.html', {
                'name': request.POST.get('Name', ''),
                'email': request.POST.get('Email', ''),
                'subject': request.POST.get('Subject', ''),
                'message': request.POST.get('Message', ''),
                'timestamp': timezone.now()
            })
            
            poruka = EmailMessage(
                subject=f"Nova poruka sa sajta: {request.POST.get('Subject', 'Bez teme')}",
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=['hasko83@gmail.com']
            )
            poruka.content_subtype = 'html'  # Enable HTML content
            poruka.send()

    # Calculate max booking date (30 days from today)
    max_date = (sada + timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    min_date = sada.strftime('%Y-%m-%d')
    
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
        'max_date': max_date,
        'min_date': min_date,
    }
    return render(request, 'appointment/jqr.html', context)


def otkazivanje(request, termin_id):
    termin = Termin.objects.get(pk=termin_id)
    termin.delete()
    return redirect('zafrizera')


@login_required(redirect_field_name='user_login/')
def zafrizera(request):
    return redirect('opcije_termini')