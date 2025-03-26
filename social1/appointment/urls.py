
from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns =[
    path('', views.zakazi, name="zakazi"),
    path('zakazi/', views.termin, name='termin'),
    path('potvrdi/', views.potvrdi, name='potvrddi'),
    path('admin1/', views.zafrizera, name='zafrizera'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_register/', views.user_register, name='user_register'),
    path('activate-user/<uidb64>/<token>', views.activate_user, name="activate"),
    path('otkazivanje/<termin_id>', views.otkazivanje, name="otkazivanje"),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('reset_password', auth_views.PasswordResetView.as_view(template_name='appointment/registration/password_reset_form.html', html_email_template_name='appointment/registration/password_reset_email.html'), 
            name="password_reset"),
    path('reset_password/done', auth_views.PasswordResetDoneView.as_view(template_name='appointment/registration/password_reset_done.html'), 
            name="password_reset_done"),    
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='appointment/registration/password_reset_confirm.html'), 
            name="password_reset_confirm"),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='appointment/registration/password_reset_complete.html'),
            name="password_reset_complete") , 
    path('opcije_termini/', views.opcije_termini, name='opcije_termini'),
    path('opcije_klijenti/', views.opcije_klijenti, name='opcije_klijenti'),
    path('opcije_izvestaj/', views.opcije_izvestaj, name='opcije_izvestaj'),

  
]