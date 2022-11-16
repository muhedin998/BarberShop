from django.shortcuts import render, redirect
from .models import Slike
from .forms import SlikaForm


def frizure(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'frizure':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/frizure.html',{"form":form,
                                                           "slike":list_katalog})

def fadeovi(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'fejdovi':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/fadeovi.html',{"form":form,
                                                           "slike":list_katalog})


def brade(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'brade':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/brade.html',{"form":form,
                                                           "slike":list_katalog})


def duga_kosa(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'duga_kosa':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/duga-kosa.html',{"form":form,
                                                           "slike":list_katalog})


def galerija(request):
    slike = Slike.objects.all()
    
    context = {'slike':slike}
    return render(request, 'galerija/katalog.html', context)

def brisanje(request, slika_id):
    slika = Slike.objects.get(pk=slika_id)
    slika.delete()
    return redirect(galerija)