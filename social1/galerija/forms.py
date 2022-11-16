from django import forms
from .models import Slike

class SlikaForm(forms.ModelForm):
    class Meta:
        model = Slike
        fields = '__all__'