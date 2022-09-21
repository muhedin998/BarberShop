from cgi import test
from multiprocessing import context
from django.shortcuts import render
from .forms import KorisnikForm, TestForm
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
    form = TestForm()

    if request.method == 'POST':
        data = TestForm(request.POST)
        if data.is_valid():
            data.save()
            value = data.cleaned_data
            print(value)

    context = {
        'godina': sada.year,
        'mesec': format(sada.month, "02d"),
        'dan': format(sada.day, "02d"),
        'form': form,
    }
    return render(request, 'appointment/jqr.html', context)