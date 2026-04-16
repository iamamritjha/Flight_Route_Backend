from __future__ import annotations

import random
from dataclasses import dataclass

from models.schemas import RunConstraints, ScenarioRequest


@dataclass
class SimulationEngine:
    constraints: RunConstraints

    def weather_factor(self) -> float:
        if not self.constraints.weather_enabled:
            return 1.0
        return float(self.constraints.weather_severity)

    def congestion_factor(self) -> float:
        if not self.constraints.congestion_enabled:
            return 1.0
        return float(self.constraints.congestion_level)

    def blocked_nodes(self) -> set[str]:
        return set(self.constraints.no_fly_airport_ids)


def build_simulation_snapshot(engine: SimulationEngine) -> dict:
    return {
        "weather_enabled": engine.constraints.weather_enabled,
        "weather_severity": engine.constraints.weather_severity,
        "congestion_enabled": engine.constraints.congestion_enabled,
        "congestion_level": engine.constraints.congestion_level,
        "no_fly_airport_ids": list(engine.constraints.no_fly_airport_ids),
        "effective_weather_factor": engine.weather_factor(),
        "effective_congestion_factor": engine.congestion_factor(),
    }


def generate_scenario(
    all_airport_ids: list[str],
    req: ScenarioRequest,
) -> RunConstraints:
    rng = random.Random(req.seed)
    n_block = max(0, int(len(all_airport_ids) * req.block_fraction))
    blocked = rng.sample(all_airport_ids, n_block) if n_block else []

    w_lo, w_hi = req.weather_severity_range
    c_lo, c_hi = req.congestion_range
    weather = round(rng.uniform(w_lo, w_hi), 3)
    congestion = round(rng.uniform(c_lo, c_hi), 3)

    return RunConstraints(
        weather_enabled=True,
        weather_severity=weather,
        congestion_enabled=True,
        congestion_level=congestion,
        no_fly_airport_ids=blocked,
    )
