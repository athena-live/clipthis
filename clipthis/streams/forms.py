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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if getattr(field.widget, 'input_type', '') == 'checkbox':
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (css + ' form-check-input').strip()
            else:
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (css + ' form-control').strip()


class ClipForm(forms.ModelForm):
    class Meta:
        model = Clip
        fields = ['url', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any context for this clip…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'paypal', 'cashapp', 'venmo',
            'btc_address', 'eth_address', 'sol_address',
            'other_handle', 'payment_note',
            # Socials
            'youtube', 'twitch', 'kick', 'tiktok', 'instagram', 'x', 'facebook', 'reddit', 'discord',
            # Pump.fun
            'pumpfun_handle',
        ]
        widgets = {
            'payment_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional payment instructions…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all widgets
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()
