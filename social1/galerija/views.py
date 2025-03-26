from django.shortcuts import render, redirect
from django.core.paginator import Paginator
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

def internet_frizure(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'internet-frizure':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/internet-frizure.html',{"form":form,
                                                           "slike":list_katalog})


def ostale_usluge(request):
    form = SlikaForm()
    slike = Slike.objects.all()
    list_katalog = []
    for sl in slike:
        if sl.kategorija == 'ostale-usluge':
            list_katalog.append(sl)

    if request.method == 'POST':
        form = SlikaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'galerija/tipovi/ostale-usluge.html',{"form":form,
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
    slike_list = Slike.objects.all()
    paginator = Paginator(slike_list, 10)  # Show 10 images per page

    page_number = request.GET.get('page')
    slike = paginator.get_page(page_number)

    context = {'slike': slike}
    return render(request, 'galerija/katalog.html', context)

def brisanje(request, slika_id):
    slika = Slike.objects.get(pk=slika_id)
    slika.delete()
    return redirect(galerija)
