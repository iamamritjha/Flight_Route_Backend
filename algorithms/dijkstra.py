from __future__ import annotations

import heapq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_dijkstra(g: nx.Graph, source: str, dest: str) -> tuple[list[str], float, float, int]:
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    dist: dict[str, float] = {source: 0.0}
    prev: dict[str, str | None] = {source: None}
    pq: list[tuple[float, str]] = [(0.0, source)]
    visited = 0

    while pq:
        d, u = heapq.heappop(pq)
        visited += 1
        if u == dest:
            break
        if d > dist.get(u, float("inf")):
            continue
        for v in g.neighbors(u):
            w = g[u][v].get("weight", 1.0)
            nd = d + float(w)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dest not in prev and source != dest:
        return [], float("inf"), 0.0, visited

    path: list[str] = []
    cur: str | None = dest
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)  # type: ignore[assignment]
    path.reverse()

    if path[0] != source:
        return [], float("inf"), 0.0, visited

    total = dist.get(dest, 0.0)
    dist_km = 0.0
    for i in range(len(path) - 1):
        dist_km += float(g[path[i]][path[i + 1]].get("distance_km", 0.0))

    return path, total, dist_km, visited
