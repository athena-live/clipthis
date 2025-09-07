from urllib.parse import urlparse
from django.core.exceptions import ValidationError


ALLOWED_STREAM_DOMAINS = {
    'youtube.com',
    'youtu.be',
    'twitch.tv',
    'kick.com',
}


def validate_stream_url(value: str) -> None:
    """Validate that URL belongs to an allowed streaming domain."""
    try:
        parsed = urlparse(value)
    except Exception as exc:
        raise ValidationError('Invalid URL.') from exc

    if parsed.scheme not in ('http', 'https'):
        raise ValidationError('URL must start with http or https.')

    host = (parsed.hostname or '').lower()
    if not host:
        raise ValidationError('URL must include a hostname.')

    # Accept exact domain or subdomains
    if not any(host == d or host.endswith(f'.{d}') for d in ALLOWED_STREAM_DOMAINS):
        raise ValidationError('Only YouTube, Twitch, or Kick links are allowed.')

