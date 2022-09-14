from django.urls import path
from . import views
urlpatterns =[
    path('', views.home, name='home'),
    path('zakazi/', views.zakazi, name="zakazi")
    
]