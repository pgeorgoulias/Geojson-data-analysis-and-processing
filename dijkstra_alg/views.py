"""HTTP form handling; route algorithms live in routing.py."""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from geopy import Nominatim
from geopy.exc import GeocoderServiceError

from .datasets import get_list
from .forms import Input
from .routing import closest, construct_results, construct_tree, dijkstra, node_coordinates


def home(request):
    return render(request, 'dijkstra_alg/main.html', {'form': Input()})


@require_http_methods(['GET', 'POST'])
def get_input(request):
    form = Input(request.POST if request.method == 'POST' else None)
    context = {'form': form, 'coord_list': []}
    if request.method == 'GET':
        return render(request, 'dijkstra_alg/main.html', context)
    if not form.is_valid():
        return render(request, 'dijkstra_alg/main.html', context, status=400)

    geocoder = Nominatim(user_agent='maritime-route-finder', timeout=10)
    locations = {}
    try:
        for field in ('start', 'end'):
            location = geocoder.geocode(form.cleaned_data[field])
            if location is None:
                form.add_error(field, 'Location not found. Try a more specific place name.')
            else:
                locations[field] = [location.longitude, location.latitude]
    except GeocoderServiceError:
        form.add_error(None, 'The location service is temporarily unavailable. Please try again.')
        return render(request, 'dijkstra_alg/main.html', context, status=503)
    if form.errors:
        return render(request, 'dijkstra_alg/main.html', context, status=400)

    features = get_list()
    coordinates = node_coordinates(features)
    if not coordinates:
        form.add_error(None, 'No routing data is currently available.')
        return render(request, 'dijkstra_alg/main.html', context, status=503)
    tree = construct_tree(list(coordinates.values()))
    node_ids = {tuple(point): node for node, point in coordinates.items()}
    start = node_ids[tuple(closest(tree, locations['start']))]
    end = node_ids[tuple(closest(tree, locations['end']))]
    route = dijkstra(start, end, features)
    if not route:
        form.add_error(None, 'No route connects these locations in the available network. Try another pair.')
        return render(request, 'dijkstra_alg/main.html', context, status=400)
    if len(route) == 1:
        context['message'] = 'Both locations map to the same network point. No route segment is needed.'
    else:
        context['coord_list'] = construct_results(route, features)
    return render(request, 'dijkstra_alg/main.html', context)
