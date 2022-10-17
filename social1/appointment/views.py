from cgi import test
from multiprocessing import context
from unicodedata import name
from django.shortcuts import render
from .forms import KorisnikForm, TestForm, FilterForm
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Usluge, Frizer, Termin

def termin(request):
    
    viewname = "termin"
    sada = datetime.now()

    termini = []
    frizeri = Frizer.objects.all()
    form = TestForm() 
    form_filter = FilterForm() 
    interval = 30
    if request.method == 'POST':
        #check if first form button is clicked
        if 'form_filter_button' in request.POST:
            form_filter = FilterForm(request.POST)
            termini = Termin.objects.filter(usluga=request.POST['usluga'], frizer=request.POST['frizer'], datum=request.POST['datum'])
            ter = f"{termini[0].vreme}".split(":")
            for ter in termini:
                vr = datetime.strptime(f"{ter.datum} {ter.vreme}",'%Y-%m-%d %H:%M:%S')
                #usl = Usluge.objects.get(pk=request.POST['usluga'])
                #zauzet = datetime(termini[0].datum,termini[0].vreme)
                #Ovo radi ! vr + usl.duzina
                #duration = timedelta(usl.duzina)
                print(vr)
                print(f"{vr + ter.usluga.duzina}")
        if 'zakazi_termin' in request.POST:
            for frizer in frizeri:
                if frizer.name == request.POST["frizer"]:
                    print(frizer)
            print(f'{request.POST["frizer"]} & {request.POST["usluga"]}')
            data = TestForm(request.POST)
            if data.is_valid():
                data.save()
                print("Form was VALID AND PASSED")
                #print(data)
            else:
                print(f"From WAS NOT VALID ! -")
                #print(data)

    context = {
        'filter_form': form_filter,
        'filtered_list': termini,
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'interval': interval,
        'frizeri': frizeri,
        'form': form,

    }
    return render(request, 'appointment/zakazivanje.html', context)

def zakazi(request):
    viewname = "zakazi"
    sada = datetime.now()

    usluge = Usluge.objects.all()
    ls1=usluge[:round(len(usluge)/3)]
    ls2= usluge[round(len(usluge)/3):round(len(usluge)/3+len(usluge)/3)]
    ls3= usluge[round(len(usluge)/3+len(usluge)/3):]

    frizeri = Frizer.objects.all()
    form = TestForm()  
    interval = 30
    if request.method == 'POST':
        for frizer in frizeri:
            if frizer.name == request.POST["frizer"]:
                print(frizer)
        print(f'{request.POST["frizer"]} & {request.POST["usluga"]}')
        data = TestForm(request.POST)
        if data.is_valid():
            data.save()
            print("Form was VALID AND PASSED")
            #print(data)
        else:
            print(f"From WAS NOT VALID ! -")
            #print(data)

    context = {
        'viewname': viewname,
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'interval': interval,
        'usluge': usluge,
        'frizeri': frizeri,
        'form': form,
        'ls1':ls1,
        'ls2':ls2,
        "ls3":ls3,
    }
    return render(request, 'appointment/jqr.html', context)