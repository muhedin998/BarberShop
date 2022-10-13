from django.urls import path
from . import views
urlpatterns =[
    path('', views.zakazi, name="zakazi"),
    path('zakazi', views.termin, name='termin')
    
]