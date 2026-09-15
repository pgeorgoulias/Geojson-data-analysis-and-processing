import math
import random
import tempfile
from pathlib import Path
from unittest.mock import patch
import json

from django.test import SimpleTestCase, override_settings

from dijkstra_alg import datasets, routing
from .helpers import segment


class RoutingTests(SimpleTestCase):
    def test_shortest_path_can_end_at_a_destination_only_node(self):
        data = [segment(1, 2), segment(2, 3)]
        self.assertEqual(routing.dijkstra(1, 3, data), [1, 2, 3])

    def test_unreachable_destination_returns_no_partial_route(self):
        data = [segment(1, 2), segment(3, 4)]
        self.assertEqual(routing.dijkstra(1, 4, data), [])

    def test_routes_respect_segment_direction(self):
        self.assertEqual(routing.dijkstra(2, 1, [segment(1, 2)]), [])

    def test_cheaper_multi_edge_route_wins(self):
        data = [segment(1, 3, 10), segment(1, 2, 2), segment(2, 3, 3)]
        self.assertEqual(routing.dijkstra(1, 3, data), [1, 2, 3])

    def test_zero_length_cycles_terminate(self):
        data = [segment(1, 2, 0), segment(2, 1, 0), segment(2, 3, 1)]
        self.assertEqual(routing.dijkstra(1, 3, data), [1, 2, 3])

    def test_no_arbitrary_limit_on_path_length(self):
        data = [segment(1, 2, 1000000), segment(2, 3, 1000000)]
        self.assertEqual(routing.dijkstra(1, 3, data), [1, 2, 3])

    def test_missing_nodes_and_empty_network_return_no_route(self):
        for start, end, data in [(1, 5, [segment(1, 2)]), (5, 2, [segment(1, 2)]), (1, 1, [])]:
            with self.subTest(start=start, end=end, data=data):
                self.assertEqual(routing.dijkstra(start, end, data), [])

    def test_same_existing_node_needs_no_edges(self):
        self.assertEqual(routing.dijkstra(2, 2, [segment(1, 2)]), [2])

    def test_duplicate_segments_use_the_shorter_length(self):
        data = [segment(1, 2, 1), segment(1, 2, 10), segment(2, 3, 1), segment(1, 3, 5)]
        self.assertEqual(routing.dijkstra(1, 3, data), [1, 2, 3])

    def test_invalid_weights_are_rejected(self):
        for weight in [-1, math.inf, math.nan]:
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    routing.create_graph([segment(1, 2, weight)])

class NearestPointTests(SimpleTestCase):
    def test_exact_matches_are_retained_for_different_tree_sizes(self):
        # The previous rounding skipped [3, 0] for five points.
        for size in range(1, 25):
            points = [[x, 0] for x in range(size)]
            tree = routing.construct_tree(points)
            for point in points:
                with self.subTest(size=size, point=point):
                    self.assertEqual(routing.closest(tree, point), point)

    def test_matches_exhaustive_coordinate_distance_search(self):
        rng = random.Random(2026)
        points = [[rng.uniform(-180, 180), rng.uniform(-80, 80)] for _ in range(150)]
        tree = routing.construct_tree(points)
        for _ in range(100):
            query = [rng.uniform(-180, 180), rng.uniform(-80, 80)]
            expected = min(points, key=lambda p: (p[0] - query[0]) ** 2 + (p[1] - query[1]) ** 2)
            self.assertEqual(routing.closest(tree, query), expected)

    def test_empty_tree_has_no_nearest_point(self):
        self.assertIsNone(routing.closest(routing.construct_tree([]), [0, 0]))

    def test_duplicate_coordinates_are_searchable(self):
        points = [[1, 2], [1, 2], [3, 4]]
        self.assertEqual(routing.closest(routing.construct_tree(points), [1, 2]), [1, 2])

class RouteGeometryTests(SimpleTestCase):
    def test_route_coordinates_follow_all_edges_in_order(self):
        data = [segment(1, 2), segment(2, 3)]
        self.assertEqual(routing.construct_results([1, 2, 3], data), [[1, 0], [2, 0], [3, 0]])

    def test_geometry_matches_the_cheapest_duplicate_segment(self):
        data = [
            segment(1, 2, 1, [[1, 0], [1.5, 0], [2, 0]]),
            segment(1, 2, 10, [[1, 0], [1.5, 5], [2, 0]]),
        ]
        self.assertEqual(routing.construct_results([1, 2], data), data[0]['geometry']['coordinates'])

    def test_missing_leg_is_not_silently_drawn_as_a_complete_route(self):
        with self.assertRaises(ValueError):
            routing.construct_results([1, 3], [segment(1, 2), segment(2, 3)])

    def test_coordinate_assembly_does_not_write_a_shared_file(self):
        with patch('builtins.open', side_effect=AssertionError('Unexpected filesystem access')):
            self.assertEqual(routing.construct_results([1, 2], [segment(1, 2)]), [[1, 0], [2, 0]])

    def test_single_node_does_not_create_an_invalid_linestring(self):
        self.assertEqual(routing.construct_results([1], [segment(1, 2)]), [])

    def test_dataset_path_is_relative_to_the_project(self):
        with tempfile.TemporaryDirectory() as directory:
            data = [segment(1, 2)]
            Path(directory, 'data').mkdir()
            Path(directory, 'data/routing-network.geojson').write_text(json.dumps({'features': data}))
            with override_settings(BASE_DIR=Path(directory)):
                self.assertEqual(datasets.get_list(), data)
