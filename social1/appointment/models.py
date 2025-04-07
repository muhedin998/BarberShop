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

    def __str__(self):
        return self.name 

class Usluge(models.Model):
    name = models.CharField(max_length=250, default="Izaberite Uslugu")
    cena = models.IntegerField(max_length=15)
    duzina = models.DurationField(default=timedelta)

    def __str__(self):
        return F"{self.name} - {self.cena}"


class Termin(models.Model):
    user  = models.ForeignKey(Korisnik, on_delete=models.CASCADE)
    frizer = models.ForeignKey(Frizer, on_delete=models.CASCADE, null=True)
    usluga = models.ForeignKey(Usluge, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    broj_telefona = models.CharField(max_length=20, blank=True, null=True)
    datum = models.DateField(blank=True, null=True)
    vreme = models.TimeField(blank=True, null=True)
    poruka = models.CharField(max_length=250, blank=True, null=True)
    cena_termina = models.IntegerField(blank=True, null=True)

def save(self, *args, **kwargs):
    if self.cena_termina is None:
        if self.usluga:
            self.cena_termina = self.usluga.cena

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
