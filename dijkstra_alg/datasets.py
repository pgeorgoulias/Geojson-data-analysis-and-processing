"""Read the canonical datasets without depending on the working directory."""

import json

from django.conf import settings


def get_list():
    """Return the original directed segments used by Dijkstra's algorithm."""
    with open(settings.BASE_DIR / 'data/routing-network.geojson', encoding='utf-8') as source:
        return json.load(source)['features']


def get_ports():
    """Return the port catalogue prepared from the bundled source workbook."""
    with open(settings.BASE_DIR / 'data/ports.geojson', encoding='utf-8') as source:
        return json.load(source)


def get_network_overlay():
    """Send only geometries to the browser; routing weights stay on the server."""
    return {
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature', 'properties': {}, 'geometry': feature['geometry']}
            for feature in get_list()
        ],
    }
