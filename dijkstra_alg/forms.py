from django import forms
from .models import PortNode


class Input(forms.Form):
    start = forms.CharField(label='Departure', max_length=100, error_messages={
        'required': 'Enter a departure location.',
        'max_length': 'Use 100 characters or fewer.',
    })
    end = forms.CharField(label='Destination', max_length=100, error_messages={
        'required': 'Enter a destination location.',
        'max_length': 'Use 100 characters or fewer.',
    })

class SubForm(forms.ModelForm):

    class Meta:
        model = PortNode
        fields = ('start', 'end')
