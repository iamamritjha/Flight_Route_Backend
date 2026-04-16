"""Compare optimal graph path vs a direct edge (when present) for fare-style recommendation."""

from __future__ import annotations

import networkx as nx


def summarize_route_recommendation(
    g: nx.Graph,
    source: str,
    destination: str,
    path: list[str],
    optimal_cost: float,
) -> tuple[float | None, float | None, str]:
    """
    Returns (direct_leg_cost_if_any, savings_vs_direct, human summary).
    `savings_vs_direct` is positive when the optimized path undercuts the direct leg.
    """
    if not path or optimal_cost == float("inf"):
        return None, None, "No feasible route under current constraints."

    direct: float | None = None
    if g.has_edge(source, destination):
        direct = float(g[source][destination]["weight"])

    oc = float(optimal_cost)

    if direct is None:
        legs = len(path) - 1
        return (
            None,
            None,
            f"No direct flight modeled between {source} and {destination}. "
            f"Best multi-hop: ₹{oc:,.0f} over {legs} segment(s).",
        )

    savings = direct - oc

    if len(path) <= 2 and abs(oc - direct) < 1e-2:
        return direct, 0.0, f"Direct nonstop is optimal at ₹{direct:,.0f}."

    if savings > 50:
        via = " → ".join(path)
        return (
            direct,
            savings,
            f"Recommended: ₹{oc:,.0f} via hub routing ({via}) vs direct ₹{direct:,.0f}. "
            f"Save about ₹{savings:,.0f}.",
        )

    if savings > 1:
        via = " → ".join(path)
        return (
            direct,
            savings,
            f"Better itinerary: ₹{oc:,.0f} ({via}) vs direct ₹{direct:,.0f}. Save ₹{savings:,.0f}.",
        )

    return (
        direct,
        max(0.0, savings),
        f"Cheapest path ₹{oc:,.0f} (direct listed at ₹{direct:,.0f}).",
    )
