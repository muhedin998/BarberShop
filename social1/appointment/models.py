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

    def __str__(self):
        return f"{self.username} - {self.dugovanje}"

class Frizer(models.Model):
    name = models.CharField(max_length=250, default='Izaberite Frizera')
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name 

class Usluge(models.Model):
    name = models.CharField(max_length=250, default="Izaberite Uslugu")
    cena = models.IntegerField()
    duzina = models.DurationField(default=timedelta)
    slika = models.ImageField(upload_to="images/usluga/", null=True, blank=True)

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
        if self.cena_termina is None:
            self.cena_termina = self.calculate_total_price()

            # Apply free appointment logic (every 15th appointment)
            if self.user and not self.user.is_superuser:
                # Count *existing* appointments (excluding the one we're about to save)
                previous_appointments = Termin.objects.filter(user=self.user).count()

                # This one will be the (previous + 1)th
                next_number = previous_appointments + 1

                if next_number % 15 == 0:
                    self.cena_termina = 0

        super().save(*args, **kwargs)

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
