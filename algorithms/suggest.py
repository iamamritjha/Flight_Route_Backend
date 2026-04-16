"""Heuristic recommendation for which path algorithm fits the scenario."""

from models.schemas import AlgorithmName, RunConstraints


def suggest_algorithm(constraints: RunConstraints) -> tuple[AlgorithmName, str]:
    """
    Rule-based suggestion (not ML): maps operational constraints to a good default.
    """
    if constraints.no_fly_airport_ids:
        return (
            "astar",
            "No-fly zones change the graph; A* uses great-circle × min-₹/km as a consistent heuristic.",
        )
    if constraints.weather_enabled and constraints.weather_severity > 1.35:
        return (
            "dijkstra",
            "Strong weather multiplier on fares: Dijkstra is robust for non-negative weighted shortest paths.",
        )
    if constraints.congestion_enabled and constraints.congestion_level > 1.6:
        return (
            "astar",
            "High congestion: A* tends to expand fewer nodes than uninformed search.",
        )
    return (
        "astar",
        "Default: A* matches Dijkstra cost here with fewer explored nodes when the heuristic is admissible.",
    )
