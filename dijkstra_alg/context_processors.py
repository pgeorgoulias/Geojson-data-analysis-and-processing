"""Expose only public map credentials to the browser."""

from django.conf import settings


def map_config(request):
    token = settings.MAPBOX_PUBLIC_TOKEN.strip()
    return {'mapbox_public_token': token if token.startswith('pk.') else ''}
