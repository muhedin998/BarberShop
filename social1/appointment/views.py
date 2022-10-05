from cgi import test
from multiprocessing import context
from unicodedata import name
from django.shortcuts import render
from .forms import KorisnikForm, TestForm
from django.http import HttpResponse
from datetime import datetime
from .models import Usluge, Frizer

def home(request):
    form = KorisnikForm()
    if request.method =='POST':
        form = KorisnikForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Korisnik je registrovan !")
    return render(request, 'appointment/index.html' , {'form':form})

def zakazi(request):
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