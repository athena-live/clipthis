from typing import Dict
from django.http import HttpRequest
from streams.models import Profile
from django.conf import settings


def theme(request: HttpRequest) -> Dict[str, str]:
    """Provide UI theme for templates: 'dark' or 'light'. Defaults to dark.

    Avoids raising if profile does not exist by creating it on demand.
    """
    try:
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            return {"theme": profile.theme, "google_tag_id": getattr(settings, 'GOOGLE_TAG_ID', '')}
    except Exception:
        pass
    return {"theme": "dark", "google_tag_id": getattr(settings, 'GOOGLE_TAG_ID', '')}
