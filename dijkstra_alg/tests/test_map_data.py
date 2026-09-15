"""Regressions for overlay data and independently cacheable map requests."""

import json
import math
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, override_settings

from dijkstra_alg import datasets
from .helpers import segment


class MapDataTests(SimpleTestCase):
    def test_port_endpoint_returns_real_catalogue_not_routing_waypoints(self):
        response = self.client.get('/api/map/ports/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/geo+json')
        ports = json.loads(response.content)['features']
        self.assertEqual(len(ports), 3582)
        self.assertEqual(ports[0]['properties']['name'], 'Watsi-Genge')
        self.assertEqual(ports[0]['properties']['country'], 'Democratic Republic of the Congo')
        self.assertEqual(ports[0]['geometry']['coordinates'], [20.62966, -0.9456])
        self.assertEqual(len({feature['id'] for feature in ports}), len(ports))
        for feature in ports:
            self.assertEqual(feature['geometry']['type'], 'Point')
            longitude, latitude = feature['geometry']['coordinates']
            self.assertTrue(math.isfinite(longitude) and -180 <= longitude <= 180)
            self.assertTrue(math.isfinite(latitude) and -90 <= latitude <= 90)

    def test_missing_country_names_and_codes_are_not_invented(self):
        ports = datasets.get_ports()['features']
        homer = next(port for port in ports if port['id'] == 4)
        self.assertEqual(homer['properties']['name'], 'Homer')
        self.assertEqual(homer['properties']['country'], '')
        self.assertEqual(homer['properties']['country_code'], 'USA')
        self.assertEqual(ports[0]['properties']['code'], '')
        self.assertEqual(sum(p['properties']['name'] == 'Unnamed port' for p in ports), 14)

    def test_network_overlay_preserves_every_segment_geometry(self):
        response = self.client.get('/api/map/network/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/geo+json')
        network = json.loads(response.content)['features']
        original = datasets.get_list()
        self.assertEqual(len(network), len(original))
        self.assertEqual(len(network), 8273)
        self.assertEqual([f['geometry'] for f in network], [f['geometry'] for f in original])
        self.assertTrue(all(f['properties'] == {} for f in network))

    def test_overlay_building_does_not_mutate_the_routing_data(self):
        feature = segment(1, 2)
        expected = json.dumps(feature, sort_keys=True)
        with patch('dijkstra_alg.datasets.get_list', return_value=[feature]):
            datasets.get_network_overlay()
        self.assertEqual(json.dumps(feature, sort_keys=True), expected)

    def test_map_data_requests_are_read_only_cacheable_and_need_no_geocoder(self):
        with patch('dijkstra_alg.views.Nominatim') as geocoder:
            for url in ['/api/map/ports/', '/api/map/network/']:
                response = self.client.get(url)
                self.assertIn('max-age=3600', response['Cache-Control'])
                self.assertEqual(self.client.post(url, {}).status_code, 405)
                self.assertEqual(self.client.put(url, {}).status_code, 405)
            geocoder.assert_not_called()

    def test_port_catalogue_uses_the_project_data_directory(self):
        catalogue = {'type': 'FeatureCollection', 'features': []}
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / 'data'
            data.mkdir()
            (data / 'ports.geojson').write_text(json.dumps(catalogue))
            with override_settings(BASE_DIR=Path(directory)):
                self.assertEqual(datasets.get_ports(), catalogue)

    def test_namespaced_assets_and_template_can_be_resolved(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'dijkstra_alg/main.html')
        for asset in ['css/planner.css', 'js/planner.js', 'js/map-overlays.js', 'js/interface.js']:
            self.assertIsNotNone(finders.find('dijkstra_alg/' + asset))
            self.assertContains(response, '/static/dijkstra_alg/' + asset)
        self.assertContains(response, 'data-ports-url="/api/map/ports/"')
        self.assertContains(response, 'data-network-url="/api/map/network/"')
