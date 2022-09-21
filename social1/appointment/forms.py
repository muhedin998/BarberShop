from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Korisnik, Termin

class KorisnikForm(UserCreationForm):
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = Korisnik
        fields = ['username', 'email', 'password1','password2', 'broj_telefona']


class DateInp(forms.DateInput):
    input_type: 'date'

class TimeInp(forms.TimeInput):
    input_type: 'time'

class TestForm(forms.ModelForm):
    class Meta:
        model = Termin
        fields = ['datum','vreme','name', 'broj_telefona']