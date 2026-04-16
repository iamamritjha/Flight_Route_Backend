from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_dfs(g: nx.Graph, source: str, dest: str) -> tuple[list[str], float, float, int]:
    """DFS finds the first valid path in depth-first order (not necessarily cheapest)."""
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    stack: list[tuple[str, list[str]]] = [(source, [source])]
    explored = 0

    while stack:
        u, path = stack.pop()
        explored += 1
        if u == dest:
            total = 0.0
            dist_km = 0.0
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                total += float(g[a][b].get("weight", 1.0))
                dist_km += float(g[a][b].get("distance_km", 0.0))
            return path, total, dist_km, explored

        for v in sorted(g.neighbors(u), reverse=True):
            if v not in path:
                stack.append((v, path + [v]))

    return [], float("inf"), 0.0, explored
