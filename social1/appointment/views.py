from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import KorisnikForm, TestForm, FilterForm
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Usluge, Frizer, Termin
import json

@login_required
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
                'usluga': usluga,
                'frizer':frizer,
                'datum':datum,
                'vreme':request.POST['vreme'],
                'name':request.POST['name'],
                'broj_telefona':request.POST['broj_telefona'],
                'uredjaj': request.COOKIES['device']
            }
            data = TestForm(params)
            if data.is_valid():
                data.save()
                messages.success(request,f"Uspešno ste zakazali termin {datum} u {request.POST['vreme']}")
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

@login_required
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

def zafrizera(request):
    termini = Termin.objects.all().order_by('datum')

    context = {'termini':termini}
    return render(request, 'appointment/zafrizera.html', context)

def register(request):

    form = KorisnikForm()
    return render(request, 'appointment/account/register.html',{'form':form})

def login(request):
    return render(request, 'appointment/account/register.html')