from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Korisnik, Termin, Review
import datetime as dt
#import django.contrib.auth.password_validation.CommonPasswordValidator

ODABIR_TERMINA = [
    (dt.time(hour=10, minute=0),"10:00"),
    (dt.time(hour=10, minute=15),"10:15"),
    (dt.time(hour=10, minute=30),"10:30"),
    (dt.time(hour=10, minute=45),"10:45"),

    (dt.time(hour=11, minute=0),"11:00"),
    (dt.time(hour=11, minute=15),"11:15"),
    (dt.time(hour=11, minute=30),"11:30"),
    (dt.time(hour=11, minute=45),"11:45"),

    (dt.time(hour=12, minute=0),"12:00"),
    (dt.time(hour=12, minute=15),"12:15"),
    (dt.time(hour=12, minute=30),"12:30"),
    (dt.time(hour=12, minute=45),"12:45"),

    (dt.time(hour=13, minute=0),"13:00"),
    (dt.time(hour=13, minute=15),"13:15"),    
    (dt.time(hour=13, minute=30),"13:30"),
    (dt.time(hour=13, minute=45),"13:45"),

    (dt.time(hour=14, minute=0),"14:00"),
    (dt.time(hour=14, minute=15),"14:15"),
    (dt.time(hour=14, minute=30),"14:30"),
    (dt.time(hour=14, minute=45),"14:45"),

    (dt.time(hour=15, minute=0),"15:00"),
    (dt.time(hour=15, minute=15),"15:15"),
    (dt.time(hour=15, minute=30),"15:30"),
    (dt.time(hour=15, minute=45),"15:45"),

    (dt.time(hour=16, minute=0),"16:00"),
    (dt.time(hour=16, minute=15),"16:15"),
    (dt.time(hour=16, minute=30),"16:30"),
    (dt.time(hour=16, minute=45),"16:45"),

    (dt.time(hour=17, minute=0),"17:00"),
    (dt.time(hour=17, minute=15),"17:15"),
    (dt.time(hour=17, minute=30),"17:30"),
    (dt.time(hour=17, minute=45),"17:45"),

    (dt.time(hour=18, minute=0),"18:00"),
    (dt.time(hour=18, minute=15),"18:15"),
    (dt.time(hour=18, minute=30),"18:30"),
    (dt.time(hour=18, minute=45),"18:45"),

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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Korisnik
        fields = ['ime_prezime', 'broj_telefona']
        
        labels = {
            'ime_prezime': 'Ime i Prezime',
            'broj_telefona': 'Broj Telefona'
        }
        
        widgets = {
            'ime_prezime': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite vaše ime i prezime'
            }),
            'broj_telefona': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite vaš broj telefona'
            })
        }

class TestForm(forms.ModelForm):
    class Meta:
        model = Termin
        fields = ['user','usluga','frizer','name','broj_telefona','datum','vreme', 'poruka', 'dodatne_usluge']
        widgets = {'vreme': forms.Select(choices=ODABIR_TERMINA,attrs={'class':'w3-select'}),
                   'poruka': forms.Textarea(attrs={'class': 'w-100 mt-1', 'placeholder': 'Ovde unesite poruku za vaseg frizera...'})}

    # def __init__(self, *args, **kwargs):
    #     super(TestForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         if visible.name == 'frizer' or visible.name == 'usluga':
    #             #print(visible.name)
    #             visible.field.widget.attrs['class'] = 'w3-select'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                attrs={'class': 'star-rating'},
                choices=Review.STAR_CHOICES
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Podelite svoje iskustvo sa nama...',
                'maxlength': 500
            })
        }
        labels = {
            'rating': 'Ocena (1-5 zvezda)',
            'comment': 'Komentar'
        }
    
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        # Make rating field required
        self.fields['rating'].required = True
        self.fields['comment'].required = True

