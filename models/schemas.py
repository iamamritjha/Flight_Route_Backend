from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Airport(BaseModel):
    id: str
    name: str
    city: str
    lat: float
    lon: float
    country: str | None = None
    region: str | None = None


AlgorithmName = Literal[
    "astar",
    "dijkstra",
    "bfs",
    "dfs",
    "bellman_ford",
    "floyd_warshall",
    "tsp",
]


class RunConstraints(BaseModel):
    weather_enabled: bool = True
    weather_severity: float = Field(1.0, ge=0.5, le=2.0, description="Multiplier when weather is on")
    congestion_enabled: bool = True
    congestion_level: float = Field(1.0, ge=1.0, le=2.5, description="Edge congestion multiplier")
    no_fly_airport_ids: list[str] = Field(default_factory=list)


class RunAlgorithmRequest(BaseModel):
    source: str
    destination: str
    algorithm: AlgorithmName
    dataset: str = "india"
    constraints: RunConstraints = Field(default_factory=RunConstraints)


class RunAlgorithmResponse(BaseModel):
    algorithm: str
    suggested_algorithm: str | None = None
    suggestion_reason: str | None = None
    path: list[str]
    cost: float
    distance_km: float
    execution_time_ms: float
    nodes_explored: int
    edges_in_path: int
    simulation: dict
    currency: str = "INR"
    direct_leg_cost: float | None = None
    savings_vs_direct: float | None = None
    recommendation_summary: str | None = None


class AlgorithmCompareRow(BaseModel):
    algorithm: str
    cost: float
    execution_time_ms: float
    nodes_explored: int
    path_length: int


class CompareResponse(BaseModel):
    source: str
    destination: str
    results: list[AlgorithmCompareRow]
    simulation: dict


class ScenarioRequest(BaseModel):
    seed: int | None = None
    block_fraction: float = Field(0.1, ge=0.0, le=0.4)
    weather_severity_range: tuple[float, float] = (1.0, 1.6)
    congestion_range: tuple[float, float] = (1.0, 1.8)
