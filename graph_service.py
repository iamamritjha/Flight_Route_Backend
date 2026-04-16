from __future__ import annotations

import json
import math
from pathlib import Path

import networkx as nx

from models.schemas import RunConstraints
from simulation.engine import SimulationEngine

DATA_PATH = Path(__file__).resolve().parent / "data" / "airports.json"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_data_path(dataset: str) -> Path:
    if dataset == "global":
        return Path(__file__).resolve().parent / "data" / "global_airports.json"
    return Path(__file__).resolve().parent / "data" / "airports.json"


def load_dataset(dataset: str = "india") -> tuple[dict[str, dict], list[dict]]:
    raw = json.loads(get_data_path(dataset).read_text(encoding="utf-8"))
    airports = {a["id"]: a for a in raw["airports"]}
    return airports, raw["routes"]


def load_meta(dataset: str = "india") -> dict:
    raw = json.loads(get_data_path(dataset).read_text(encoding="utf-8"))
    return raw.get("meta") or {}


def edge_effective_cost(
    base_fuel: float,
    distance_km: float,
    engine: SimulationEngine,
) -> float:
    w = engine.weather_factor()
    c = engine.congestion_factor()
    return base_fuel * w * c


def build_weighted_graph(
    constraints: RunConstraints,
    dataset: str = "india"
) -> tuple[nx.Graph, dict[str, dict], SimulationEngine]:
    airports, routes = load_dataset(dataset)
    engine = SimulationEngine(constraints)
    blocked = engine.blocked_nodes()

    g = nx.Graph()
    for aid, a in airports.items():
        if aid in blocked:
            continue
        g.add_node(aid, **a)

    for r in routes:
        u, v = r["from"], r["to"]
        if u in blocked or v in blocked:
            continue
        if u not in g or v not in g:
            continue
        dist = float(r["distance_km"])
        fuel = float(r["base_fuel_cost"])
        cost = edge_effective_cost(fuel, dist, engine)
        g.add_edge(u, v, weight=cost, distance_km=dist, base_fuel=fuel)

    return g, airports, engine


def heuristic_fn(airports: dict[str, dict], dest: str, g: nx.Graph):
    """
    Admissible heuristic: great-circle distance (km) * minimum observed INR/km on edges.
    Any route's cost is at least min_ratio times path length in km (for edges meeting that ratio).
    """
    dest_a = airports[dest]
    ratios: list[float] = []
    for _, _, d in g.edges(data=True):
        dk = float(d.get("distance_km") or 0.0)
        if dk > 0:
            ratios.append(float(d.get("weight", 0.0)) / dk)
    min_ratio = min(ratios) if ratios else 0.0

    def h(node: str) -> float:
        if node not in airports or min_ratio <= 0:
            return 0.0
        a = airports[node]
        dkm = haversine_km(a["lat"], a["lon"], dest_a["lat"], dest_a["lon"])
        return dkm * min_ratio

    return h
