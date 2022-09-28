from email.policy import default
import imp
from tkinter.messagebox import RETRY
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

class Korisnik(AbstractUser):
    broj_telefona = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return self.username

class Frizer(models.Model):
    name = models.CharField(max_length=250, default='Izaberite Frizera')
    image = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.name 

class Usluge(models.Model):
    name = models.CharField(max_length=250, default="Izaberite Uslugu")
    cena = models.CharField(max_length=15)
    duzina = models.DurationField(default=timedelta)

    def __str__(self):
        return F"{self.name} - {self.cena}"


class Termin(models.Model):
    frizer = models.ForeignKey(Frizer, on_delete=models.CASCADE, null=True)
    usluga = models.ForeignKey(Usluge, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=250, blank=True)
    broj_telefona = models.CharField(max_length=20, default=0)
    datum = models.DateField(blank=True, null=True)
    vreme = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.datum},{self.vreme}"


    def __str__(self):
        return self.name