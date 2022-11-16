from django.urls import path
from . import views


urlpatterns = [
    path('katalog', views.galerija, name='galerija'),

    path('frizure', views.frizure, name='frizure'),

    path('brade', views.brade, name='brade'),

    path('fadeovi', views.fadeovi, name='fadeovi'),

    path('duga-kosa', views.duga_kosa, name='duga-kosa'),

    path('brisanje/<slika_id>', views.brisanje, name='brisanje')
]
