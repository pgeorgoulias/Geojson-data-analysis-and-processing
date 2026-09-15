import json
import re
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.utils import translation
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

from .helpers import location, segment


@override_settings(ALLOWED_HOSTS=['testserver'])
class RouteViewTests(SimpleTestCase):
    def setUp(self):
        self.features = [segment(1, 2), segment(2, 3)]
        self.data_patch = patch('dijkstra_alg.views.get_list', return_value=self.features)
        self.get_data = self.data_patch.start()
        self.addCleanup(self.data_patch.stop)
        self.geocoder_patch = patch('dijkstra_alg.views.Nominatim')
        self.geocoder_class = self.geocoder_patch.start()
        self.addCleanup(self.geocoder_patch.stop)
        self.geocode = self.geocoder_class.return_value.geocode
        self.geocode.side_effect = [location(1), location(2)]

    def post_route(self, **changes):
        data = {'start': 'Start port', 'end': 'End port'}
        data.update(changes)
        return self.client.post('/input', data)

    def test_home_and_direct_input_get_render_without_geocoding(self):
        for path in ['/', '/input']:
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), 'name="start"')
        self.geocode.assert_not_called()

    @override_settings(MAPBOX_PUBLIC_TOKEN='pk.example.signature')
    def test_public_map_token_is_supplied_on_home_and_route_responses(self):
        for response in [self.client.get('/'), self.post_route()]:
            payload = re.search(r'<script id="mapbox-public-token" type="application/json">(.*?)</script>', response.content.decode(), re.S)
            self.assertEqual(json.loads(payload.group(1)), 'pk.example.signature')

    @override_settings(MAPBOX_PUBLIC_TOKEN='sk.private-example')
    def test_secret_map_token_is_never_rendered(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'sk.private-example')
        self.assertContains(response, '<script id="mapbox-public-token" type="application/json">""</script>', html=True)

    @override_settings(MAPBOX_PUBLIC_TOKEN='')
    def test_route_calculation_still_works_without_a_map_token(self):
        response = self.post_route()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coord_list'], [[1, 0], [2, 0]])

    def test_selected_destination_maps_to_its_own_node(self):
        response = self.post_route()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coord_list'], [[1, 0], [2, 0]])
        self.assertContains(response, 'value="End port"')
        self.get_data.assert_called_once()

    def test_destination_only_endpoint_is_reachable(self):
        self.geocode.side_effect = [location(1), location(3)]
        response = self.post_route()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coord_list'], [[1, 0], [2, 0], [3, 0]])

    def test_non_exact_locations_snap_to_the_nearest_network_points(self):
        self.geocode.side_effect = [location(1.1), location(2.9)]
        response = self.post_route()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coord_list'], [[1, 0], [2, 0], [3, 0]])

    def test_map_receives_valid_json_coordinates(self):
        response = self.post_route()
        payload = re.search(r'<script id="route-coordinates" type="application/json">(.*?)</script>', response.content.decode(), re.S)
        self.assertIsNotNone(payload)
        self.assertEqual(json.loads(payload.group(1)), response.context['coord_list'])
        self.assertContains(response, '/static/dijkstra_alg/js/planner.js')
        self.assertContains(response, 'id="map"')

    def test_unknown_locations_show_field_errors(self):
        for answers, field in [([None, location(2)], 'start'), ([location(1), None], 'end')]:
            with self.subTest(field=field):
                self.geocode.side_effect = answers
                response = self.post_route()
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.context['form'].errors)
                self.assertContains(response, 'Location not found', status_code=400)
        self.get_data.assert_not_called()

    def test_empty_missing_and_too_long_inputs_are_validated_before_geocoding(self):
        for data in [{}, {'start': 'Port'}, {'start': '  ', 'end': 'Port'}, {'start': 'x' * 101, 'end': 'Port'}]:
            with self.subTest(data=data):
                self.assertEqual(self.client.post('/input', data).status_code, 400)
        self.geocode.assert_not_called()

    def test_geocoder_failures_show_retry_message(self):
        for error in [GeocoderTimedOut('timeout'), GeocoderServiceError('unavailable')]:
            with self.subTest(error=type(error).__name__):
                self.geocode.side_effect = error
                response = self.post_route()
                self.assertContains(response, 'location service is temporarily unavailable', status_code=503)
        self.get_data.assert_not_called()

    def test_unreachable_route_has_message_and_no_route_payload(self):
        self.geocode.side_effect = [location(3), location(1)]
        response = self.post_route()
        self.assertContains(response, 'No route connects these locations', status_code=400)
        self.assertNotContains(response, 'id="route-coordinates"', status_code=400)
        self.assertEqual(response.context['coord_list'], [])

    def test_same_network_point_has_message_and_no_invalid_line(self):
        self.geocode.side_effect = [location(2), location(2)]
        response = self.post_route()
        self.assertContains(response, 'Both locations map to the same network point')
        self.assertNotContains(response, 'id="route-coordinates"')
        self.assertEqual(response.context['coord_list'], [])

    def test_empty_dataset_has_clear_message(self):
        self.get_data.return_value = []
        self.assertContains(self.post_route(), 'No routing data is currently available', status_code=503)

    def test_submitted_values_remain_html_escaped(self):
        self.geocode.side_effect = [None, location(2)]
        response = self.post_route(start='"><script>alert(1)</script>')
        self.assertNotContains(response, '<script>alert(1)</script>', status_code=400)
        self.assertContains(response, '&lt;script&gt;', status_code=400)

    def test_other_http_methods_are_rejected(self):
        self.assertEqual(self.client.put('/input').status_code, 405)
        self.geocode.assert_not_called()

    def test_validation_messages_stay_english_with_a_greek_browser_language(self):
        with translation.override('el'):
            response = self.client.post('/input', {}, HTTP_ACCEPT_LANGUAGE='el-GR,el;q=0.9')
        self.assertContains(response, 'Enter a departure location.', status_code=400)
        self.assertContains(response, 'Enter a destination location.', status_code=400)
        self.geocode.assert_not_called()
