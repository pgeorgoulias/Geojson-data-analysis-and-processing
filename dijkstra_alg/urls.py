from django.urls import path
from . import map_views, views

urlpatterns = [
    path('', views.home, name="input"),
    path('input', views.get_input, name="output"),
    path('api/map/ports/', map_views.ports, name='map-ports'),
    path('api/map/network/', map_views.network, name='map-network'),
]
