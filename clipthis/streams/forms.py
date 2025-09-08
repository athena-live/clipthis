from django import forms
from .models import StreamLink, Clip, Profile


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


class ClipForm(forms.ModelForm):
    class Meta:
        model = Clip
        fields = ['url', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any context for this clip…'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'paypal', 'cashapp', 'venmo',
            'btc_address', 'eth_address', 'sol_address',
            'other_handle', 'payment_note',
        ]
        widgets = {
            'payment_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional payment instructions…'}),
        }
