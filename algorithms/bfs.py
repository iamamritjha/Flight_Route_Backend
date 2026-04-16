from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_bfs(g: nx.Graph, source: str, dest: str) -> tuple[list[str], float, float, int]:
    """BFS minimizes hop count on the unweighted view of the graph."""
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    q: deque[str] = deque([source])
    parent: dict[str, str | None] = {source: None}
    explored = 0

    while q:
        u = q.popleft()
        explored += 1
        if u == dest:
            break
        for v in g.neighbors(u):
            if v not in parent:
                parent[v] = u
                q.append(v)

    if dest not in parent:
        return [], float("inf"), 0.0, explored

    path: list[str] = []
    cur: str | None = dest
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)  # type: ignore[assignment]
    path.reverse()

    total = 0.0
    dist_km = 0.0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        total += float(g[a][b].get("weight", 1.0))
        dist_km += float(g[a][b].get("distance_km", 0.0))

    return path, total, dist_km, explored
