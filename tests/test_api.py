from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_airports():
    r = client.get("/airports")
    assert r.status_code == 200
    data = r.json()
    assert len(data["airports"]) == 32


def test_routes():
    r = client.get("/routes")
    assert r.status_code == 200
    assert len(r.json()["routes"]) >= 50


def test_weather_airport():
    r = client.get("/weather", params={"airport_id": "DEL"})
    assert r.status_code == 200
    data = r.json()
    assert "wind_speed_kmh" in data
    assert "conditions" in data


def test_del_hyd_hub_recommendation():
    """Direct DEL-HYD is expensive; Dijkstra should prefer cheaper hub path."""
    body = {
        "source": "DEL",
        "destination": "HYD",
        "algorithm": "dijkstra",
        "constraints": {"weather_enabled": False, "congestion_enabled": False},
    }
    r = client.post("/run-algorithm", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["cost"] < 25000
    assert len(out["path"]) >= 3
    assert out["savings_vs_direct"] is not None and out["savings_vs_direct"] > 0


def test_run_dijkstra():
    body = {
        "source": "DEL",
        "destination": "HYD",
        "algorithm": "dijkstra",
        "constraints": {
            "weather_enabled": True,
            "congestion_enabled": True,
        },
    }
    r = client.post("/run-algorithm", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["path"][0] == "DEL" and out["path"][-1] == "HYD"
    assert out["suggested_algorithm"]
    assert out.get("recommendation_summary")


def test_compare():
    r = client.get("/compare", params={"source": "DEL", "destination": "HYD"})
    assert r.status_code == 200
    rows = r.json()["results"]
    names = {x["algorithm"] for x in rows}
    assert "dijkstra" in names and "tsp" in names


def test_scenario():
    r = client.post("/scenario", json={"seed": 42, "block_fraction": 0.05})
    assert r.status_code == 200
    assert "constraints" in r.json()
