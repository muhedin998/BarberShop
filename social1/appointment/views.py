from multiprocessing import context
from django.shortcuts import render
from .forms import KorisnikForm
from django.http import HttpResponse
from datetime import datetime

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
    context = {
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': sada.day,
    }
    return render(request, 'appointment/zakazivanje.html', context)