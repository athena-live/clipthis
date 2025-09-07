from django import forms
from .models import StreamLink


class StreamLinkForm(forms.ModelForm):
    class Meta:
        model = StreamLink
        fields = [
            'url',
            'active',
            'notes',
            'tip_amount',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notes for clippers (what to look for)...'}),
        }

