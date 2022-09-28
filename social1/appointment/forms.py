from tkinter import Widget
from tkinter.tix import Select
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
        fields = ['usluga','frizer','datum','vreme','name', 'broj_telefona']

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name == 'frizer' or visible.name == 'usluga':
                #print(visible.name)
                visible.field.widget.attrs['class'] = 'w3-select'