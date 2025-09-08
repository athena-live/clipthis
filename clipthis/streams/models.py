from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings as django_settings
from .validators import validate_stream_url, validate_no_links
from .utils import extract_youtube_id, fetch_youtube_video


class StreamLink(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stream_links')
    url = models.URLField(max_length=500, validators=[validate_stream_url])
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Cached YouTube metadata (optional)
    yt_video_id = models.CharField(max_length=16, blank=True)
    yt_title = models.CharField(max_length=300, blank=True)
    yt_channel = models.CharField(max_length=200, blank=True)
    yt_thumbnail = models.URLField(blank=True)
    yt_published_at = models.DateTimeField(null=True, blank=True)
    yt_view_count = models.BigIntegerField(default=0)
    yt_like_count = models.BigIntegerField(default=0)
    yt_duration = models.CharField(max_length=32, blank=True)
    yt_cached_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.owner} – {self.url}"

    def _is_youtube(self) -> bool:
        u = (self.url or '').lower()
        return 'youtube.com' in u or 'youtu.be' in u

    def refresh_youtube_cache(self, force: bool = False) -> None:
        if not self._is_youtube():
            return
        vid = extract_youtube_id(self.url)
        if not vid:
            return
        # Check staleness
        max_age_hours = getattr(django_settings, 'YOUTUBE_CACHE_HOURS', 24)
        now = timezone.now()
        if not force and self.yt_cached_at and (now - self.yt_cached_at).total_seconds() < max_age_hours * 3600:
            return
        data = fetch_youtube_video(getattr(django_settings, 'YOUTUBE_API_KEY', ''), vid)
        if not data:
            return
        self.yt_video_id = vid
        self.yt_title = data.get('title') or ''
        self.yt_channel = data.get('channelTitle') or ''
        self.yt_thumbnail = data.get('thumbnail') or ''
        pub = data.get('publishedAt')
        try:
            if pub:
                # ISO8601 date
                self.yt_published_at = timezone.datetime.fromisoformat(pub.replace('Z', '+00:00'))
        except Exception:
            pass
        self.yt_view_count = int(data.get('viewCount') or 0)
        self.yt_like_count = int(data.get('likeCount') or 0)
        self.yt_duration = data.get('duration') or ''
        self.yt_cached_at = now
        # Save only cached fields to avoid racing owner/url
        self.save(update_fields=[
            'yt_video_id','yt_title','yt_channel','yt_thumbnail','yt_published_at',
            'yt_view_count','yt_like_count','yt_duration','yt_cached_at'
        ])


class Clip(models.Model):
    stream = models.ForeignKey(StreamLink, on_delete=models.CASCADE, related_name='clips')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_clips')
    url = models.URLField(max_length=500, validators=[validate_stream_url])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Cached YouTube metadata (optional)
    yt_video_id = models.CharField(max_length=16, blank=True)
    yt_title = models.CharField(max_length=300, blank=True)
    yt_channel = models.CharField(max_length=200, blank=True)
    yt_thumbnail = models.URLField(blank=True)
    yt_published_at = models.DateTimeField(null=True, blank=True)
    yt_view_count = models.BigIntegerField(default=0)
    yt_like_count = models.BigIntegerField(default=0)
    yt_duration = models.CharField(max_length=32, blank=True)
    yt_cached_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Clip for {self.stream_id} by {self.submitter_id}"

    def _is_youtube(self) -> bool:
        u = (self.url or '').lower()
        return 'youtube.com' in u or 'youtu.be' in u

    def refresh_youtube_cache(self, force: bool = False) -> None:
        if not self._is_youtube():
            return
        vid = extract_youtube_id(self.url)
        if not vid:
            return
        max_age_hours = getattr(django_settings, 'YOUTUBE_CACHE_HOURS', 24)
        now = timezone.now()
        if not force and self.yt_cached_at and (now - self.yt_cached_at).total_seconds() < max_age_hours * 3600:
            return
        data = fetch_youtube_video(getattr(django_settings, 'YOUTUBE_API_KEY', ''), vid)
        if not data:
            return
        self.yt_video_id = vid
        self.yt_title = data.get('title') or ''
        self.yt_channel = data.get('channelTitle') or ''
        self.yt_thumbnail = data.get('thumbnail') or ''
        pub = data.get('publishedAt')
        try:
            if pub:
                self.yt_published_at = timezone.datetime.fromisoformat(pub.replace('Z', '+00:00'))
        except Exception:
            pass
        self.yt_view_count = int(data.get('viewCount') or 0)
        self.yt_like_count = int(data.get('likeCount') or 0)
        self.yt_duration = data.get('duration') or ''
        self.yt_cached_at = now
        self.save(update_fields=[
            'yt_video_id','yt_title','yt_channel','yt_thumbnail','yt_published_at',
            'yt_view_count','yt_like_count','yt_duration','yt_cached_at'
        ])


class StreamRating(models.Model):
    UP = 1
    DOWN = -1
    VALUE_CHOICES = (
        (UP, 'Up'),
        (DOWN, 'Down'),
    )

    stream = models.ForeignKey(StreamLink, on_delete=models.CASCADE, related_name='stream_ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stream_ratings')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('stream', 'user'),)


class ClipRating(models.Model):
    UP = 1
    DOWN = -1
    VALUE_CHOICES = (
        (UP, 'Up'),
        (DOWN, 'Down'),
    )

    clip = models.ForeignKey(Clip, on_delete=models.CASCADE, related_name='clip_ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clip_ratings')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('clip', 'user'),)


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

    # Social media / streaming handles (no links)
    youtube = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    twitch = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    kick = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    tiktok = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    instagram = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    x = models.CharField(max_length=120, blank=True, validators=[validate_no_links], help_text='X (formerly Twitter)')
    facebook = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    reddit = models.CharField(max_length=120, blank=True, validators=[validate_no_links])
    discord = models.CharField(max_length=120, blank=True, validators=[validate_no_links], help_text='Discord username or server handle')
    pumpfun_handle = models.CharField(max_length=120, blank=True, validators=[validate_no_links], help_text='pump.fun handle (no links)')

    PLAN_FREE = 'free'
    PLAN_PLUS = 'plus'
    PLAN_PREMIUM = 'premium'
    PLAN_CHOICES = (
        (PLAN_FREE, 'Free'),
        (PLAN_PLUS, 'Plus'),
        (PLAN_PREMIUM, 'Premium'),
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    plan_set_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def plan_limit(plan: str) -> int:
        limits = {
            Profile.PLAN_FREE: 50,
            Profile.PLAN_PLUS: 200,
            Profile.PLAN_PREMIUM: 500,
        }
        return limits.get(plan or Profile.PLAN_FREE, 50)

    @staticmethod
    def vote_limit(plan: str) -> int:
        """Maximum number of active votes (stream + clip) a user may place based on plan."""
        limits = {
            Profile.PLAN_FREE: 100,
            Profile.PLAN_PLUS: 1000,
            Profile.PLAN_PREMIUM: 5000,
        }
        return limits.get(plan or Profile.PLAN_FREE, 100)

    THEME_DARK = 'dark'
    THEME_LIGHT = 'light'
    THEME_CHOICES = (
        (THEME_DARK, 'Dark'),
        (THEME_LIGHT, 'Light'),
    )
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default=THEME_DARK)


class BillingTransaction(models.Model):
    PLAN_CHOICES = (
        ('plus', 'Plus'),
        ('premium', 'Premium'),
    )

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELED = 'canceled'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_FAILED, 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_transactions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount_cents = models.IntegerField()
    currency = models.CharField(max_length=10, default='usd')
    stripe_session_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user_id} {self.plan} {self.status}"

    def __str__(self) -> str:
        return f"Profile for {self.user_id}"
