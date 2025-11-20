from django.contrib import admin
from .models import Korisnik,  Termin, Usluge, Usluge, Frizer, Duznik, Notification, FCMToken, Review, Banner, GalleryImage

admin.site.register(Korisnik)
admin.site.register(Termin)
admin.site.register(Frizer)
admin.site.register(Duznik)
admin.site.register(Notification)

@admin.register(Usluge)
class UslugeAdmin(admin.ModelAdmin):
    list_display = ['name', 'kategorija', 'cena', 'duzina']
    list_filter = ['kategorija']
    search_fields = ['name']
    ordering = ['kategorija', 'name']

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


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    actions = ['activate_images', 'deactivate_images']
    
    fieldsets = (
        ('Slika', {
            'fields': ('image', 'image_preview')
        }),
        ('Informacije', {
            'fields': ('title', 'description', 'order', 'is_active')
        }),
        ('Sistemske informacije', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 300px;" />'
        return "Nema slike"
    image_preview.short_description = "Pregled slike"
    image_preview.allow_tags = True
    
    def activate_images(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} slika je aktivirano.")
    activate_images.short_description = "Aktiviraj izabrane slike"
    
    def deactivate_images(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} slika je deaktivirano.")
    deactivate_images.short_description = "Deaktiviraj izabrane slike"


