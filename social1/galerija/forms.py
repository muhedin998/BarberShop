from django import forms
from .models import Slike

class SlikaForm(forms.ModelForm):
    slika = forms.ImageField(required=True)
    class Meta:
        model = Slike
        fields = '__all__'