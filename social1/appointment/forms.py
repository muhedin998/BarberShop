import imp
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Korisnik

class KorisnikForm(UserCreationForm):
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = Korisnik
        fields = ['username', 'email', 'password1','password2', 'broj_telefona']