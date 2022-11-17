from django.shortcuts import render, redirect
from .models import Slike
from .forms import SlikaForm


def krace_moderne(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'krace-moderne':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/frizure.html',{"form":form,
                                                           "slike":list_katalog})

def duze_moderne(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'duze-moderne':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/fadeovi.html',{"form":form,
                                                           "slike":list_katalog})


def decije_frizure(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'decije-frizure':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/brade.html',{"form":form,
                                                           "slike":list_katalog})


def tribali(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'tribali':
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