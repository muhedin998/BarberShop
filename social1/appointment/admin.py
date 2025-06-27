from django.contrib import admin
from .models import Korisnik,  Termin, Usluge, Usluge, Frizer, Duznik, Notification, FCMToken

admin.site.register(Korisnik)
admin.site.register(Termin)
admin.site.register(Usluge)
admin.site.register(Frizer)
admin.site.register(Duznik)
admin.site.register(Notification)

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'device_id']
    readonly_fields = ['token', 'created_at', 'updated_at']


