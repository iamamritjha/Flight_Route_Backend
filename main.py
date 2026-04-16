from __future__ import annotations


import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from algorithms import (
    run_astar,
    run_bellman_ford,
    run_bfs,
    run_dfs,
    run_dijkstra,
    run_floyd_warshall,
    run_tsp,
    suggest_algorithm,
)
from graph_service import build_weighted_graph, heuristic_fn, load_dataset, load_meta
from models.schemas import (
    AlgorithmCompareRow,
    CompareResponse,
    RunAlgorithmRequest,
    RunAlgorithmResponse,
    RunConstraints,
    ScenarioRequest,
)
from routing.recommend import summarize_route_recommendation
from services.weather import fetch_weather_snapshot
from simulation.engine import build_simulation_snapshot, generate_scenario

ALGORITHMS_PATH = [
    "astar",
    "dijkstra",
    "bfs",
    "dfs",
    "bellman_ford",
    "floyd_warshall",
]


def dispatch_algorithm(name: str, g, source: str, dest: str, airports: dict):
    h = heuristic_fn(airports, dest, g)
    if name == "astar":
        return run_astar(g, source, dest, h)
    if name == "dijkstra":
        return run_dijkstra(g, source, dest)
    if name == "bfs":
        return run_bfs(g, source, dest)
    if name == "dfs":
        return run_dfs(g, source, dest)
    if name == "bellman_ford":
        return run_bellman_ford(g, source, dest)
    if name == "floyd_warshall":
        return run_floyd_warshall(g, source, dest)
    if name == "tsp":
        return run_tsp(g, source, dest)
    raise ValueError(f"Unknown algorithm: {name}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_dataset()
    yield


app = FastAPI(
    title="Flight Route Optimization API",
    description="India & South Asia airport graph — hub-aware routing, simulation, live weather (Open-Meteo).",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "flight-route-optimization", "docs": "/docs"}


@app.get("/airports")
def list_airports(dataset: str = "india"):
    airports, _ = load_dataset(dataset)
    return {"airports": list(airports.values())}


@app.get("/routes")
def list_routes(dataset: str = "india"):
    _, routes = load_dataset(dataset)
    return {"routes": [{"from": r["from"], "to": r["to"]} for r in routes]}


@app.get("/meta")
def meta(dataset: str = "india"):
    return load_meta(dataset)


@app.get("/weather")
def weather(
    lat: float | None = None,
    lon: float | None = None,
    airport_id: str | None = None,
    dataset: str = "india",
):
    airports, _ = load_dataset(dataset)
    if airport_id:
        if airport_id not in airports:
            raise HTTPException(404, f"Unknown airport: {airport_id}")
        a = airports[airport_id]
        lat, lon = float(a["lat"]), float(a["lon"])
    if lat is None or lon is None:
        raise HTTPException(400, "Provide both lat and lon, or airport_id")
    try:
        return fetch_weather_snapshot(lat, lon)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Weather service error: {e}") from e


@app.post("/run-algorithm", response_model=RunAlgorithmResponse)
def run_algorithm(body: RunAlgorithmRequest):
    g, airports, engine = build_weighted_graph(body.constraints, body.dataset)
    src, dst = body.source, body.destination

    if src not in g:
        raise HTTPException(400, f"Source airport unavailable or in no-fly zone: {src}")
    if body.algorithm != "tsp" and dst not in g:
        raise HTTPException(400, f"Destination airport unavailable or in no-fly zone: {dst}")

    sug_name, sug_reason = suggest_algorithm(body.constraints)

    t0 = time.perf_counter()
    path, cost, dist_km, nodes_explored = dispatch_algorithm(
        body.algorithm, g, src, dst, airports
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    edges = max(0, len(path) - 1) if path else 0

    direct_cost, savings, rec_summary = summarize_route_recommendation(g, src, dst, path, float(cost))
    currency = str(load_meta(body.dataset).get("currency") or "INR")

    return RunAlgorithmResponse(
        algorithm=body.algorithm,
        suggested_algorithm=sug_name,
        suggestion_reason=sug_reason,
        path=path,
        cost=float(cost),
        distance_km=float(dist_km),
        execution_time_ms=round(elapsed_ms, 4),
        nodes_explored=int(nodes_explored),
        edges_in_path=edges,
        simulation=build_simulation_snapshot(engine),
        currency=currency,
        direct_leg_cost=direct_cost,
        savings_vs_direct=savings,
        recommendation_summary=rec_summary,
    )


@app.get("/compare", response_model=CompareResponse)
def compare(source: str, destination: str, weather_enabled: bool = True, congestion_enabled: bool = True, dataset: str = "india"):
    constraints = RunConstraints(
        weather_enabled=weather_enabled,
        congestion_enabled=congestion_enabled,
    )
    g, airports, engine = build_weighted_graph(constraints, dataset)

    if source not in g or destination not in g:
        raise HTTPException(400, "Source or destination invalid for current simulation graph.")

    rows: list[AlgorithmCompareRow] = []
    for name in ALGORITHMS_PATH:
        t0 = time.perf_counter()
        path, cost, _, nodes_explored = dispatch_algorithm(name, g, source, destination, airports)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        rows.append(
            AlgorithmCompareRow(
                algorithm=name,
                cost=float(cost),
                execution_time_ms=round(elapsed_ms, 4),
                nodes_explored=int(nodes_explored),
                path_length=len(path),
            )
        )


    return CompareResponse(
        source=source,
        destination=destination,
        results=rows,
        simulation=build_simulation_snapshot(engine),
    )


@app.post("/scenario")
def create_scenario(body: ScenarioRequest, dataset: str = "india"):
    airports, _ = load_dataset(dataset)
    ids = [a["id"] for a in airports.values()]
    constraints = generate_scenario(ids, body)
    return {"constraints": constraints.model_dump()}


@app.get("/suggest")
def suggest(weather_enabled: bool = True, congestion_enabled: bool = True):
    c = RunConstraints(weather_enabled=weather_enabled, congestion_enabled=congestion_enabled)
    name, reason = suggest_algorithm(c)
    return {"algorithm": name, "reason": reason}
