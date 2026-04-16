from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_bellman_ford(g: nx.Graph, source: str, dest: str) -> tuple[list[str], float, float, int]:
    """Single-source shortest paths; allows negative weights (none in our dataset)."""
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    nodes = list(g.nodes())
    n = len(nodes)
    idx = {nodes[i]: i for i in range(n)}
    dist = [float("inf")] * n
    prev: list[int | None] = [None] * n
    dist[idx[source]] = 0.0
    relaxations = 0

    for _ in range(n - 1):
        updated = False
        for u, v, data in g.edges(data=True):
            w = float(data.get("weight", 1.0))
            iu, iv = idx[u], idx[v]
            if dist[iu] + w < dist[iv]:
                dist[iv] = dist[iu] + w
                prev[iv] = iu
                updated = True
                relaxations += 1
            if dist[iv] + w < dist[iu]:
                dist[iu] = dist[iv] + w
                prev[iu] = iv
                updated = True
                relaxations += 1
        if not updated:
            break

    idest = idx[dest]
    if dist[idest] == float("inf"):
        return [], float("inf"), 0.0, relaxations

    path_ids: list[int] = []
    cur: int | None = idest
    while cur is not None:
        path_ids.append(cur)
        cur = prev[cur]
    path_ids.reverse()
    path = [nodes[i] for i in path_ids]

    total = dist[idest]
    dist_km = 0.0
    for i in range(len(path) - 1):
        dist_km += float(g[path[i]][path[i + 1]].get("distance_km", 0.0))

    nodes_explored = n * (n - 1)
    return path, total, dist_km, nodes_explored
