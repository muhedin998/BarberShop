from django.contrib import admin
from .models import Korisnik,  Termin, Usluge, Usluge, Frizer, Duznik, Notification, FCMToken, Review

admin.site.register(Korisnik)
admin.site.register(Termin)
admin.site.register(Usluge)
admin.site.register(Frizer)
admin.site.register(Duznik)
admin.site.register(Notification)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__username', 'user__ime_prezime', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} recenzija je odobreno.")
    approve_reviews.short_description = "Odobri izabrane recenzije"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} recenzija je odbačeno.")
    disapprove_reviews.short_description = "Odbaci izabrane recenzije"

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'device_id']
    readonly_fields = ['token', 'created_at', 'updated_at']


