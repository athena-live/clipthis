from django.conf import settings
from django.db import models
from .validators import validate_stream_url, validate_no_links


class StreamLink(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stream_links')
    url = models.URLField(max_length=500, validators=[validate_stream_url])
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.owner} – {self.url}"


class Clip(models.Model):
    stream = models.ForeignKey(StreamLink, on_delete=models.CASCADE, related_name='clips')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_clips')
    url = models.URLField(max_length=500, validators=[validate_stream_url])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Clip for {self.stream_id} by {self.submitter_id}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    # Payment handles (no links)
    paypal = models.CharField(max_length=120, blank=True, validators=[validate_no_links], help_text='PayPal email or handle (no links)')
    cashapp = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    venmo = models.CharField(max_length=120, blank=True, validators=[validate_no_links])

    # Common crypto wallet addresses
    btc_address = models.CharField(max_length=128, blank=True, validators=[validate_no_links])
    eth_address = models.CharField(max_length=128, blank=True, validators=[validate_no_links])
    sol_address = models.CharField(max_length=128, blank=True, validators=[validate_no_links])

    other_handle = models.CharField(max_length=200, blank=True, validators=[validate_no_links])
    payment_note = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Profile for {self.user_id}"
