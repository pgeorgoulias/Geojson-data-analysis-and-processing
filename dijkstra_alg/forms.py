from django import forms
from .models import PortNode


class Input(forms.Form):
    start = forms.CharField(label='start', max_length=100)
    end = forms.CharField(label='end', max_length=100)

class SubForm(forms.ModelForm):

    class Meta:
        model = PortNode
        fields = ('start', 'end')
