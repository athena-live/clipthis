from django.conf import settings
from django.db import models
from .validators import validate_stream_url


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
