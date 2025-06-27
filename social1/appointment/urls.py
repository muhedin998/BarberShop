
from django.urls import path, reverse_lazy
from . import views
from . import fcm_views
from . import test_views
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
    path('opcije_istorija/', views.opcije_istorija, name='opcije_istorija'),
    path('obrisi_duznika/<duznik_id>', views.obrisi_duznika, name='obrisi_duznika'),
    path('profile-page/', views.profile_page, name='profile_page'),
    path('notifications-page/', views.notifications_page, name='notifications_page'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-unread/<int:notification_id>/', views.mark_notification_unread, name='mark_notification_unread'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # FCM endpoints
    path('fcm/register-token/', fcm_views.register_fcm_token, name='register_fcm_token'),
    path('fcm/unregister-token/', fcm_views.unregister_fcm_token, name='unregister_fcm_token'),
    path('fcm/token-status/', fcm_views.fcm_token_status, name='fcm_token_status'),
    
    # Test endpoints (admin only)
    path('admin/create-test-notification/', test_views.create_test_notification, name='create_test_notification'),
    
    # Debug endpoints
    path('debug/fcm/', views.fcm_debug_page, name='fcm_debug_page'),

  
]