from __future__ import annotations

import heapq
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import networkx as nx


def run_astar(
    g: nx.Graph,
    source: str,
    dest: str,
    heuristic: Callable[[str], float],
) -> tuple[list[str], float, float, int]:
    if source not in g or dest not in g:
        return [], float("inf"), 0.0, 0

    open_heap: list[tuple[float, float, str]] = [(heuristic(source), 0.0, source)]
    g_score: dict[str, float] = {source: 0.0}
    came: dict[str, str | None] = {source: None}
    explored = 0

    while open_heap:
        _, g_cur, u = heapq.heappop(open_heap)
        explored += 1
        if u == dest:
            break
        if g_cur > g_score.get(u, float("inf")):
            continue
        for v in g.neighbors(u):
            w = float(g[u][v].get("weight", 1.0))
            tg = g_cur + w
            if tg < g_score.get(v, float("inf")):
                g_score[v] = tg
                came[v] = u
                f = tg + heuristic(v)
                heapq.heappush(open_heap, (f, tg, v))

    if dest not in came:
        return [], float("inf"), 0.0, explored

    path: list[str] = []
    cur: str | None = dest
    while cur is not None:
        path.append(cur)
        cur = came.get(cur)  # type: ignore[assignment]
    path.reverse()

    total = g_score.get(dest, float("inf"))
    dist_km = 0.0
    for i in range(len(path) - 1):
        dist_km += float(g[path[i]][path[i + 1]].get("distance_km", 0.0))

    return path, total, dist_km, explored
