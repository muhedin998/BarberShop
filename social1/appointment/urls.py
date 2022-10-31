from django.urls import path
from . import views
urlpatterns =[
    path('', views.zakazi, name="zakazi"),
    path('zakazi/', views.termin, name='termin'),
    path('potvrdi/', views.potvrdi, name='potvrddi'),
    path('admin1/', views.zafrizera, name='zafrizera'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_register/', views.user_register, name='user_register')
]