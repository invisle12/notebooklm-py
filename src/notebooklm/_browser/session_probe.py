"""Signed-in probes for the Playwright login capture.

Kept out of :mod:`.browser_capture` (a shrink-only module-size baseline) so the
capture flow only carries the call sites.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from ..config import get_base_url

GOOGLE_SIGN_IN_URL = "https://accounts.google.com/ServiceLogin"

# Google session cookies whose presence means the browser profile is signed in.
_GOOGLE_SESSION_COOKIE_NAMES = frozenset({"SID", "__Secure-1PSID"})


def context_has_google_session(context: Any) -> bool:
    """Return whether ``context`` holds a ``.google.com`` session cookie.

    Landing on the app host is not proof of sign-in: since the Gemini Notebook
    rebrand Google serves the app shell to signed-out visitors too, so the
    host check alone captured an empty jar and reported "Already logged in".
    Fails open (True) when the jar cannot be read, preserving the host-only
    behaviour rather than forcing a sign-in on a read error.
    """
    try:
        cookies = context.storage_state().get("cookies", [])
        return any(
            cookie.get("name") in _GOOGLE_SESSION_COOKIE_NAMES
            and str(cookie.get("domain", "")).lstrip(".") == "google.com"
            and cookie.get("value")
            for cookie in cookies
        )
    except Exception:  # noqa: BLE001 - diagnostic probe, never fatal
        return True


def google_sign_in_url() -> str:
    """Return Google's sign-in URL that continues to the configured app host."""
    return f"{GOOGLE_SIGN_IN_URL}?{urlencode({'continue': f'{get_base_url()}/'})}"
