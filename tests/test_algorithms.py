import networkx as nx

from algorithms import (
    run_astar,
    run_bellman_ford,
    run_bfs,
    run_dfs,
    run_dijkstra,
    run_floyd_warshall,
    run_tsp,
)
from graph_service import build_weighted_graph, heuristic_fn
from models.schemas import RunConstraints


def _small_graph():
    g = nx.Graph()
    g.add_edge("A", "B", weight=1.0, distance_km=100)
    g.add_edge("B", "C", weight=2.0, distance_km=200)
    g.add_edge("A", "C", weight=10.0, distance_km=500)
    return g


def test_dijkstra_shortest():
    g = _small_graph()
    path, cost, _, _ = run_dijkstra(g, "A", "C")
    assert path == ["A", "B", "C"]
    assert cost == 3.0


def test_astar_matches_dijkstra_on_dataset():
    g, airports, _ = build_weighted_graph(RunConstraints())
    src, dst = "DEL", "HYD"
    h = heuristic_fn(airports, dst, g)
    _, c1, _, _ = run_dijkstra(g, src, dst)
    _, c2, _, _ = run_astar(g, src, dst, h)
    assert abs(c1 - c2) < 1e-2


def test_bfs_min_hops():
    g = _small_graph()
    path, _, _, _ = run_bfs(g, "A", "C")
    assert path == ["A", "C"]


def test_integration_graph_connected():
    g, _, _ = build_weighted_graph(RunConstraints())
    assert nx.is_connected(g)


def test_path_algorithms_reach_dest():
    g, airports, _ = build_weighted_graph(RunConstraints())
    src, dst = "DEL", "HYD"
    h = heuristic_fn(airports, dst, g)
    for fn, args in [
        (run_dijkstra, (g, src, dst)),
        (run_astar, (g, src, dst, h)),
        (run_bfs, (g, src, dst)),
        (run_dfs, (g, src, dst)),
        (run_bellman_ford, (g, src, dst)),
        (run_floyd_warshall, (g, src, dst)),
    ]:
        path, cost, _, _ = fn(*args)
        assert path[0] == src and path[-1] == dst
        assert cost < float("inf")


def test_tsp_returns_tour():
    g, _, _ = build_weighted_graph(RunConstraints())
    path, cost, _, _ = run_tsp(g, "DEL", "DEL")
    assert path[0] == path[-1] == "DEL"
    assert len(set(path[:-1])) == g.number_of_nodes()
    assert cost < float("inf")
