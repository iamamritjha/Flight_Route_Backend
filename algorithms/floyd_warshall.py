from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_floyd_warshall(g: nx.Graph, source: str, dest: str) -> tuple[list[str], float, float, int]:
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    nodes = list(g.nodes())
    n = len(nodes)
    idx = {nodes[i]: i for i in range(n)}
    inf = float("inf")
    d = [[inf] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        d[i][i] = 0.0

    for u, v, data in g.edges(data=True):
        w = float(data.get("weight", 1.0))
        i, j = idx[u], idx[v]
        d[i][j] = w
        d[j][i] = w
        nxt[i][j] = j
        nxt[j][i] = i

    explored = 0
    for k in range(n):
        for i in range(n):
            for j in range(n):
                explored += 1
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    nxt[i][j] = nxt[i][k]

    isrc, idst = idx[source], idx[dest]
    if d[isrc][idst] == inf:
        return [], float("inf"), 0.0, explored

    path: list[str] = []
    cur = isrc
    while cur != idst:
        path.append(nodes[cur])
        nxt_cur = nxt[cur][idst]
        if nxt_cur is None:
            return [], float("inf"), 0.0, explored
        cur = nxt_cur
    path.append(nodes[idst])

    total = d[isrc][idst]
    dist_km = 0.0
    for i in range(len(path) - 1):
        dist_km += float(g[path[i]][path[i + 1]].get("distance_km", 0.0))

    return path, total, dist_km, explored
