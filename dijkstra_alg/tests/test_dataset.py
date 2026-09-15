from unittest.mock import patch

from django.test import SimpleTestCase

from dijkstra_alg import datasets, routing
from .helpers import location


class IncludedDatasetTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.features = datasets.get_list()

    def test_every_included_endpoint_can_be_found_exactly(self):
        points = list(routing.node_coordinates(self.features).values())
        tree = routing.construct_tree(points)
        for point in points:
            self.assertEqual(routing.closest(tree, point), point)

    def test_regression_route_contains_only_existing_connections(self):
        route = routing.dijkstra(79, 103, self.features)
        self.assertGreaterEqual(len(route), 3)
        self.assertEqual((route[0], route[-1]), (79, 103))
        graph = routing.create_graph(self.features)
        for start, end in zip(route, route[1:]):
            self.assertIn(end, graph[start])
        points = routing.construct_results(route, self.features)
        nodes = routing.node_coordinates(self.features)
        self.assertEqual(points[0], nodes[79])
        self.assertEqual(points[-1], nodes[103])

    def test_included_route_renders_through_the_complete_django_request(self):
        nodes = routing.node_coordinates(self.features)
        answers = [location(*nodes[node]) for node in [79, 103]]
        with patch('dijkstra_alg.views.Nominatim') as geocoder:
            geocoder.return_value.geocode.side_effect = answers
            response = self.client.post('/input', {'start': 'Start port', 'end': 'End port'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coord_list'][0], nodes[79])
        self.assertEqual(response.context['coord_list'][-1], nodes[103])
        self.assertContains(response, 'route-coordinates')
