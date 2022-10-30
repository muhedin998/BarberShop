from django.urls import path
from . import views
urlpatterns =[
    path('', views.zakazi, name="zakazi"),
    path('zakazi/', views.termin, name='termin'),
    path('potvrdi/', views.potvrdi, name='potvrddi'),
    path('admin1/', views.zafrizera, name='zafrizera'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register')
]