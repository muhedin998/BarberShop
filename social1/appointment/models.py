from io import open_code
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

class Korisnik(AbstractUser):
    ime_prezime = models.CharField(max_length=220, blank=True, null=True)
    broj_telefona = models.CharField(max_length=20,blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    dugovanje = models.IntegerField(default=0)
    loyalty_appointment_count = models.IntegerField(default=0, help_text="Number of appointments counted toward loyalty program (every 15th is free)")

    def __str__(self):
        return f"{self.username} - {self.dugovanje}"

class Frizer(models.Model):
    name = models.CharField(max_length=250, default='Izaberite Frizera')
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name 

class Usluge(models.Model):
    KATEGORIJA_CHOICES = [
        ('sisanje', 'Šišanje'),
        ('brada', 'Brada'),
        ('ostale_usluge', 'Ostale usluge'),
        ('vip_usluge', 'Vip usluge'),
    ]
    
    name = models.CharField(max_length=250, default="Izaberite Uslugu")
    cena = models.IntegerField()
    duzina = models.DurationField(default=timedelta)
    slika = models.ImageField(upload_to="images/usluga/", null=True, blank=True)
    kategorija = models.CharField(max_length=50, choices=KATEGORIJA_CHOICES, default='sisanje')

    def __str__(self):
            return F"{self.name}"

class FCMToken(models.Model):
    user = models.ForeignKey("Korisnik", on_delete=models.CASCADE)
    token = models.CharField(max_length=500, unique=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'device_id']

    def __str__(self):
        return f"FCM Token for {self.user.username} - {self.device_id}"

class Notification(models.Model):
    user = models.ForeignKey("Korisnik", on_delete=models.CASCADE)  # recipient
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    push_sent = models.BooleanField(default=False)  # Track if push notification was sent

    def __str__(self):
        return f"{self.title} to {self.user.username}, created at {self.created_at}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Send push notification for new notifications
        if is_new and not self.push_sent:
            self.send_push_notification()
    
    def send_push_notification(self):
        """Send push notification to user when notification is created"""
        try:
            from .push_notifications import send_push_notification_to_user
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f'Attempting to send push notification for notification {self.id} to user {self.user.username}')
            
            result = send_push_notification_to_user(
                user=self.user,
                title=self.title,
                body=self.message,
                data={
                    'notification_id': str(self.id),
                    'type': 'appointment_notification'
                }
            )
            
            logger.info(f'Push notification result for notification {self.id}: {result}')
            
            if result:
                # Use update() to avoid triggering save() again and prevent infinite loop
                Notification.objects.filter(id=self.id).update(push_sent=True)
                logger.info(f'Push notification sent successfully for notification {self.id}')
            else:
                logger.warning(f'Push notification failed for notification {self.id} - no FCM tokens or send failed')
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send push notification for notification {self.id}: {str(e)}', exc_info=True)


class Termin(models.Model):
    user  = models.ForeignKey(Korisnik, on_delete=models.CASCADE)
    frizer = models.ForeignKey(Frizer, on_delete=models.CASCADE, null=True)
    usluga = models.ForeignKey(Usluge, on_delete=models.CASCADE, null=True)
    dodatne_usluge = models.JSONField(default=list, blank=True, null=True)  # Lista ID-jeva dodatnih usluga
    name = models.CharField(max_length=250, blank=True, null=True)
    broj_telefona = models.CharField(max_length=20, blank=True, null=True)
    datum = models.DateField(blank=True, null=True)
    vreme = models.TimeField(blank=True, null=True)
    poruka = models.CharField(max_length=250, blank=True, null=True)
    cena_termina = models.IntegerField(blank=True, null=True)
    
    @property
    def effective_price(self):
        """Returns the effective price for this appointment (cena_termina if available, otherwise calculated)"""
        if self.cena_termina is not None:
            return self.cena_termina
        return self.calculate_total_price()
    
    def calculate_total_price(self):
        """Calculate total price without saving"""
        total_cena = 0
        
        # Add main service price
        if self.usluga:
            total_cena += self.usluga.cena
        
        # Add additional services prices
        if self.dodatne_usluge:
            dodatne_usluge_objects = Usluge.objects.filter(id__in=self.dodatne_usluge)
            for dodatna_usluga in dodatne_usluge_objects:
                total_cena += dodatna_usluga.cena
        
        return total_cena
    
    @property
    def has_multiple_services(self):
        """Check if appointment has additional services"""
        return bool(self.dodatne_usluge)
    
    @property
    def all_services(self):
        """Get all services (main + additional) with their info"""
        services = []
        if self.usluga:
            services.append({
                'name': self.usluga.name,
                'price': self.usluga.cena,
                'is_main': True
            })
        
        if self.dodatne_usluge:
            dodatne_usluge_objects = Usluge.objects.filter(id__in=self.dodatne_usluge)
            for usluga in dodatne_usluge_objects:
                services.append({
                    'name': usluga.name,
                    'price': usluga.cena,
                    'is_main': False
                })
        
        return services

    def save(self, *args, **kwargs):
        from django.db import transaction

        is_new = self.pk is None

        if self.cena_termina is None:
            self.cena_termina = self.calculate_total_price()

            # Apply free appointment logic (every 15th appointment)
            if self.user and not self.user.is_superuser and is_new:
                # Use loyalty counter instead of counting all appointments
                with transaction.atomic():
                    # Lock the user row to prevent race conditions
                    user = Korisnik.objects.select_for_update().get(pk=self.user.pk)

                    # Increment loyalty counter
                    user.loyalty_appointment_count += 1
                    next_number = user.loyalty_appointment_count

                    # Check if this is a free appointment
                    if next_number % 15 == 0:
                        self.cena_termina = 0

                    # Save user with updated counter
                    user.save(update_fields=['loyalty_appointment_count'])

        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        from django.db import transaction
        
        # Decrement loyalty counter when appointment is cancelled
        if self.user and not self.user.is_superuser:
            with transaction.atomic():
                # Lock the user row to prevent race conditions
                user = Korisnik.objects.select_for_update().get(pk=self.user.pk)
                
                # Only decrement if counter is greater than 0
                if user.loyalty_appointment_count > 0:
                    user.loyalty_appointment_count -= 1
                    user.save(update_fields=['loyalty_appointment_count'])
        
        super().delete(*args, **kwargs)

    class Meta:
        unique_together = ['datum','vreme','frizer']

    def __str__(self):
        return f"{self.user.ime_prezime},{self.datum},{self.vreme}"


class Duznik(models.Model):
    user = models.ForeignKey("Korisnik", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, blank=True) 
    broj_telefona = models.CharField(max_length=200, blank=True)  
    duguje = models.IntegerField(null=True, blank=True)
    datum_upisa = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.name else (self.user.ime_prezime if self.user and hasattr(self.user, 'ime_prezime') else "Nema ime")


class Review(models.Model):
    STAR_CHOICES = [
        (1, '1 Zvezda'),
        (2, '2 Zvezde'),
        (3, '3 Zvezde'),
        (4, '4 Zvezde'),
        (5, '5 Zvezda'),
    ]
    
    user = models.OneToOneField("Korisnik", on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=STAR_CHOICES)
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)  # For potential moderation
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.ime_prezime} - {self.rating} zvezda"
    
    @property
    def user_initials(self):
        """Get user initials for avatar display"""
        if self.user.ime_prezime:
            parts = self.user.ime_prezime.strip().split()
            if len(parts) >= 2:
                return f"{parts[0][0].upper()}{parts[-1][0].upper()}"
            elif len(parts) == 1:
                return f"{parts[0][0].upper()}"
        return "U"  # Default if no name
    
    @property
    def star_range(self):
        """Get range for displaying stars in template"""
        return range(1, 6)
    
    @property
    def filled_stars(self):
        """Get range for filled stars"""
        return range(1, self.rating + 1)
    
    @property 
    def empty_stars(self):
        """Get range for empty stars"""
        return range(self.rating + 1, 6)


class Banner(models.Model):
    title = models.CharField(max_length=200, verbose_name="Naslov banera")
    text = models.TextField(max_length=500, verbose_name="Tekst banera")
    start_date = models.DateTimeField(verbose_name="Početak prikazivanja")
    end_date = models.DateTimeField(verbose_name="Kraj prikazivanja")
    is_active = models.BooleanField(default=True, verbose_name="Aktivan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Banner"
        verbose_name_plural = "Banneri"
    
    def __str__(self):
        if self.start_date and self.end_date:
            return f"{self.title} ({self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')})"
        return self.title
    
    @property
    def is_currently_active(self):
        """Check if banner should be displayed right now"""
        from django.utils import timezone
        if not self.start_date or not self.end_date:
            return False
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    @classmethod
    def get_active_banners(cls):
        """Get all currently active banners"""
        from django.utils import timezone
        now = timezone.now()
        return cls.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')


class GalleryImage(models.Model):
    image = models.ImageField(upload_to="images/gallery/", verbose_name="Slika")
    title = models.CharField(max_length=200, blank=True, verbose_name="Naslov")
    description = models.TextField(max_length=500, blank=True, verbose_name="Opis")
    order = models.IntegerField(default=0, verbose_name="Redosled prikazivanja")
    is_active = models.BooleanField(default=True, verbose_name="Aktivan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Slika iz galerije"
        verbose_name_plural = "Slike iz galerije"
    
    def __str__(self):
        return self.title if self.title else f"Slika {self.id}"
