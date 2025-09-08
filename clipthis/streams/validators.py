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


def validate_no_links(value: str) -> None:
    """Ensure the value does not look like a URL/link."""
    if not value:
        return
    lower = str(value).strip().lower()
    if lower.startswith(('http://', 'https://', 'www.')) or '://' in lower:
        raise ValidationError('Links are not allowed here; use plain handles or addresses.')


def validate_pumpfun_url(value: str) -> None:
    """Ensure URL points to pump.fun."""
    if not value:
        return
    try:
        parsed = urlparse(value)
    except Exception as exc:
        raise ValidationError('Invalid URL.') from exc
    if parsed.scheme not in ('http', 'https'):
        raise ValidationError('URL must start with http or https.')
    host = (parsed.hostname or '').lower()
    if not host:
        raise ValidationError('URL must include a hostname.')
    if not (host == 'pump.fun' or host.endswith('.pump.fun')):
        raise ValidationError('Only pump.fun URLs are allowed in this field.')
