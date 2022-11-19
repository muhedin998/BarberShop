from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Korisnik, Termin
import datetime as dt
#import django.contrib.auth.password_validation.CommonPasswordValidator

ODABIR_TERMINA = [
    (dt.time(hour=10, minute=0),"10:00"),
    (dt.time(hour=10, minute=20),"10:20"),
    (dt.time(hour=10, minute=40),"10:40"),
    (dt.time(hour=11, minute=0),"11:00"),
    (dt.time(hour=11, minute=20),"11:20"),
    (dt.time(hour=11, minute=40),"11:40"),
    (dt.time(hour=12, minute=0),"12:00"),
    (dt.time(hour=12, minute=20),"12:20"),
    (dt.time(hour=12, minute=40),"12:40"),
    (dt.time(hour=13, minute=0),"13:00"),
    (dt.time(hour=13, minute=20),"13:20"),
    (dt.time(hour=13, minute=40),"13:40"),
    (dt.time(hour=14, minute=0),"14:00"),
    (dt.time(hour=14, minute=20),"14:20"),
    (dt.time(hour=14, minute=40),"14:40"),
    (dt.time(hour=15, minute=0),"15:00"),
    (dt.time(hour=15, minute=20),"15:20"),
    (dt.time(hour=15, minute=40),"15:40"),
    (dt.time(hour=16, minute=0),"16:00"),
    (dt.time(hour=16, minute=20),"16:20"),
    (dt.time(hour=16, minute=40),"16:40"),
    (dt.time(hour=17, minute=0),"17:00"),
    (dt.time(hour=17, minute=20),"17:20"),
    (dt.time(hour=17, minute=40),"17:40"),
    (dt.time(hour=18, minute=0),"18:00"),
    (dt.time(hour=18, minute=20),"18:20"),
    (dt.time(hour=18, minute=40),"18:40"),

]

class FilterForm(forms.Form):
    class Meta:
        model = Termin
        fields = ['usluga', 'frizer', 'datum']

my_default_errors = {
    'required': "Ovo polje je obavezno",
    'invalid': "Nepravilan Unos !"
}
class KorisnikForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(),label="Unesite sifru")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Potvrda sifre")

    class Meta:
        model = Korisnik
        fields = ['ime_prezime', 'username', 'email', 'broj_telefona','password']
        
        labels ={
            'username': "Vase korisicko ime", 
        }
        error_messages = {
            'username':{
                "unique": "Korisnicko ime je zauzeto"
            },
            'email':{
                "unique":"Email adresa je zauzeta"
            }
        }

    def clean(self):
        cleaned_data = super(KorisnikForm, self).clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        
        if len(password) < 8 or len(password2) < 8:
            self.add_error('password',"Lozinka mora sadrzati 8 karaktera")

        if password != password2:
           self.add_error('password2', "Sifre se ne podudaraju !")
    
    def __init__(self, *args, **kwargs):
        super(KorisnikForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-select'

class TestForm(forms.ModelForm):
    class Meta:
        model = Termin
        fields = ['user','usluga','frizer','name','broj_telefona','datum','vreme']
        widgets = {'vreme': forms.Select(choices=ODABIR_TERMINA,attrs={'class':'w3-select'})}

    # def __init__(self, *args, **kwargs):
    #     super(TestForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         if visible.name == 'frizer' or visible.name == 'usluga':
    #             #print(visible.name)
    #             visible.field.widget.attrs['class'] = 'w3-select'

