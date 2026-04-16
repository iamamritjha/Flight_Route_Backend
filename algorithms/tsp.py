from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    pass


def _leg_cost_and_dist(g: nx.Graph, u: str, v: str) -> tuple[float, float]:
    if g.has_edge(u, v):
        e = g[u][v]
        return float(e.get("weight", 0.0)), float(e.get("distance_km", 0.0))
    path = nx.shortest_path(g, u, v, weight="weight")
    cost = 0.0
    dkm = 0.0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        cost += float(g[a][b].get("weight", 0.0))
        dkm += float(g[a][b].get("distance_km", 0.0))
    return cost, dkm


def run_tsp(g: nx.Graph, source: str, destination: str) -> tuple[list[str], float, float, int]:
    """
    Greedy nearest-neighbor TSP: visit every airport once, return to source.
    `destination` is ignored (tour is closed); kept for API compatibility.
    """
    nodes = list(g.nodes())
    if len(nodes) < 2:
        return [source], 0.0, 0.0, 1

    if not nx.is_connected(g):
        return [], float("inf"), 0.0, len(nodes)

    if source not in g:
        return [], float("inf"), 0.0, 0

    unvisited = set(nodes)
    unvisited.remove(source)
    tour = [source]
    current = source
    explored = 0

    while unvisited:
        explored += len(unvisited)
        best_v = None
        best_len = float("inf")
        for v in unvisited:
            try:
                pl = nx.shortest_path_length(g, current, v, weight="weight")
            except nx.NetworkXNoPath:
                pl = float("inf")
            if pl < best_len:
                best_len = pl
                best_v = v
        if best_v is None:
            return [], float("inf"), 0.0, explored
        tour.append(best_v)
        unvisited.remove(best_v)
        current = best_v

    tour.append(source)

    total = 0.0
    dist_km = 0.0
    for i in range(len(tour) - 1):
        c, d = _leg_cost_and_dist(g, tour[i], tour[i + 1])
        total += c
        dist_km += d

    return tour, total, dist_km, explored
