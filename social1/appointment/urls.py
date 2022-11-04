
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns =[
    path('', views.zakazi, name="zakazi"),
    path('zakazi/', views.termin, name='termin'),
    path('potvrdi/', views.potvrdi, name='potvrddi'),
    path('admin1/', views.zafrizera, name='zafrizera'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_register/', views.user_register, name='user_register'),
    path('otkazivanje/<termin_id>', views.otkazivanje, name="otkazivanje"),
    path('reset_password', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('reset_password/done', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),    
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete")   


]