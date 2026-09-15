"""Read-only GeoJSON endpoints for the map's independent display layers."""

from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from .datasets import get_network_overlay, get_ports


@require_GET
@cache_control(public=True, max_age=3600)
def ports(request):
    return JsonResponse(get_ports(), content_type='application/geo+json',
                        json_dumps_params={'separators': (',', ':')})


@require_GET
@cache_control(public=True, max_age=3600)
def network(request):
    return JsonResponse(get_network_overlay(), content_type='application/geo+json',
                        json_dumps_params={'separators': (',', ':')})
