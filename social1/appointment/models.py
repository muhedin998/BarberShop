import imp
from tkinter.messagebox import RETRY
from django.db import models
from django.contrib.auth.models import AbstractUser

class Korisnik(AbstractUser):
    broj_telefona = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return self.username

class Termin(models.Model):
    name = models.CharField(max_length=250, blank=True)
    broj_telefona = models.CharField(max_length=20, default=0)
    datum = models.DateField(blank=True)
    vreme = models.TimeField(blank=True)

    def __str__(self):
        return f"{self.datum},{self.vreme}"

class Test():
    trajanje = models.DurationField()

class Usluge(models.Model):
    name = models.CharField(max_length=250)
    cena = models.CharField(max_length=15)
    duzina = models.DurationField()

    def __str__(self):
        return self.name