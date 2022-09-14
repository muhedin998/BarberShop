import imp
from django.db import models
from django.contrib.auth.models import AbstractUser

class Korisnik(AbstractUser):
    broj_telefona = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return self.username