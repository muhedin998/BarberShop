from django.urls import path
from . import views


urlpatterns = [
    path('katalog', views.galerija, name='galerija'),

    path('krace-moderne', views.krace_moderne, name='krace-moderne'),

    path('duze-moderne', views.duze_moderne, name='duze-moderne'),

    path('decije-frizure', views.decije_frizure, name='decije-frizure'),

    path('tribali', views.tribali, name='tribali'),

    path('ostale-usluge', views.ostale_usluge, name='ostale-usluge'),

    path('internet-frizure', views.internet_frizure, name='internet-frizure'),

    

    path('brisanje/<slika_id>', views.brisanje, name='brisanje')
]
