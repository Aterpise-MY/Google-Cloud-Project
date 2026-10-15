"""Optional Cloud CDN cache invalidation (pages are also served with a short max-age)."""
from __future__ import annotations


def make_invalidator(project: str, url_map: str):
    if not (project and url_map):
        return None

    def invalidate() -> None:
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        r = AuthorizedSession(creds).post(
            f"https://compute.googleapis.com/compute/v1/projects/{project}/global/urlMaps/{url_map}/invalidateCache",
            json={"path": "/*"}, timeout=30)
        r.raise_for_status()

    return invalidate
