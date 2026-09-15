"""Shortest-path and nearest-point algorithms for the directed route network."""

import heapq
import math

from .datasets import get_list


def create_graph(features=None):
    """Build a directed graph, including nodes with no outgoing segments."""
    if features is None:
        features = get_list()
    graph = {}
    for feature in features:
        properties = feature['properties']
        start = properties['From Node0']
        end = properties['To Node0']
        distance = properties['Length0']
        if not math.isfinite(distance) or distance < 0:
            raise ValueError('Route lengths must be finite and non-negative.')
        neighbors = graph.setdefault(start, {})
        graph.setdefault(end, {})
        # Multiple segments may connect the same pair of nodes.
        neighbors[end] = min(distance, neighbors.get(end, math.inf))
    return graph


def node_coordinates(features):
    """Associate each node ID with its own endpoint coordinates."""
    coordinates = {}
    for feature in features:
        properties = feature['properties']
        points = feature['geometry']['coordinates']
        coordinates[properties['From Node0']] = points[0]
        coordinates[properties['To Node0']] = points[-1]
    return coordinates


def pop_parsed_data():
    """Return every network point, including destination-only endpoints."""
    return list(node_coordinates(get_list()).values())


def dijkstra(start, end, features=None):
    """Return the shortest directed path, or [] when no path exists."""
    graph = create_graph(features)
    if start not in graph or end not in graph:
        return []
    distances = {start: 0}
    previous = {}
    pending = [(0, start)]

    while pending:
        distance, current = heapq.heappop(pending)
        if distance != distances[current]:
            continue
        if current == end:
            route = [end]
            while route[-1] != start:
                route.append(previous[route[-1]])
            return list(reversed(route))
        for neighbor, length in graph[current].items():
            candidate = distance + length
            if candidate < distances.get(neighbor, math.inf):
                distances[neighbor] = candidate
                previous[neighbor] = current
                heapq.heappush(pending, (candidate, neighbor))
    return []


def construct_results(route, features=None):
    """Assemble map coordinates from the same segments used to weight the graph."""
    if len(route) < 2:
        return []
    if features is None:
        features = get_list()
    segments = {}
    for feature in features:
        properties = feature['properties']
        edge = (properties['From Node0'], properties['To Node0'])
        if (edge not in segments or
                properties['Length0'] < segments[edge]['properties']['Length0']):
            segments[edge] = feature

    coordinates = []
    for edge in zip(route, route[1:]):
        if edge not in segments:
            raise ValueError('The route contains a connection missing from the dataset.')
        points = segments[edge]['geometry']['coordinates']
        if coordinates and coordinates[-1] == points[0]:
            coordinates.extend(points[1:])
        else:
            coordinates.extend(points)
    # Coordinates belong to this request; no shared output file is overwritten.
    return coordinates


def construct_tree(nodes, height=0):
    """Build a two-dimensional search tree without dropping or duplicating points."""
    if not nodes:
        return None
    axis = height % 2
    ordered = sorted(nodes, key=lambda point: point[axis])
    middle = len(ordered) // 2
    return {
        'node': ordered[middle],
        'left': construct_tree(ordered[:middle], height + 1),
        'right': construct_tree(ordered[middle + 1:], height + 1),
    }


def _distance_squared(first, second):
    return sum((a - b) ** 2 for a, b in zip(first, second))


def compare(point, first, second):
    """Return the nearer candidate using the existing coordinate-distance metric."""
    if first is None:
        return second
    if second is None:
        return first
    if _distance_squared(point, first) <= _distance_squared(point, second):
        return first
    return second


def closest(tree, point, height=0):
    """Find the nearest coordinate, checking the other branch when necessary."""
    if tree is None:
        return None
    axis = height % 2
    offset = point[axis] - tree['node'][axis]
    near, far = ('right', 'left') if offset > 0 else ('left', 'right')
    best = compare(point, closest(tree[near], point, height + 1), tree['node'])
    if _distance_squared(point, best) > offset ** 2:
        best = compare(point, closest(tree[far], point, height + 1), best)
    return best
