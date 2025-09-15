from django.contrib import admin
from .models import Korisnik,  Termin, Usluge, Usluge, Frizer, Duznik, Notification, FCMToken, Review, Banner

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

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'is_currently_active_display', 'created_at']
    list_filter = ['is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'text']
    readonly_fields = ['created_at', 'updated_at', 'is_currently_active_display']
    date_hierarchy = 'start_date'
    actions = ['activate_banners', 'deactivate_banners']
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('title', 'text', 'is_active')
        }),
        ('Vremenske postavke', {
            'fields': ('start_date', 'end_date')
        }),
        ('Sistemske informacije', {
            'fields': ('is_currently_active_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_currently_active_display(self, obj):
        return obj.is_currently_active
    is_currently_active_display.short_description = "Trenutno aktivan"
    is_currently_active_display.boolean = True
    
    def activate_banners(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} banner(a) je aktivirano.")
    activate_banners.short_description = "Aktiviraj izabrane bannere"
    
    def deactivate_banners(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} banner(a) je deaktivirano.")
    deactivate_banners.short_description = "Deaktiviraj izabrane bannere"


