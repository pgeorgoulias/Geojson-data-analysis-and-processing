from types import SimpleNamespace


def segment(start, end, length=1, coordinates=None):
    return {
        'type': 'Feature',
        'properties': {'From Node0': start, 'To Node0': end, 'Length0': length},
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates or [[start, 0], [end, 0]],
        },
    }


def location(longitude, latitude=0):
    return SimpleNamespace(longitude=longitude, latitude=latitude)
