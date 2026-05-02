"""
ROI & Profit Optimization Calculator.
Simulates revenue/profit at different price points using price elasticity of demand.
"""
import math
from app.schemas.roi import ROIInput, ROIOutput, PriceScenario


def simulate_roi(data: ROIInput) -> ROIOutput:
    """
    Simulate profit/revenue at multiple price points using price elasticity.

    Demand model: Q(p) = Q0 * (p / p0) ^ e
    where e = price_elasticity (typically -1.0 to -2.5)
    """
    p0 = data.selling_price
    q0 = data.monthly_units
    cost = data.cost_price
    e = data.price_elasticity

    def demand_at(price: float) -> float:
        if price <= 0:
            return 0.0
        return max(0.0, q0 * math.pow(price / p0, e))

    def make_scenario(price: float) -> PriceScenario:
        units = demand_at(price)
        revenue = price * units
        gross_profit = (price - cost) * units
        margin = ((price - cost) / price * 100) if price > 0 else 0
        current_revenue = p0 * q0
        current_profit = (p0 - cost) * q0
        return PriceScenario(
            price=round(price, 2),
            units=round(units, 1),
            revenue=round(revenue, 2),
            gross_profit=round(gross_profit, 2),
            margin_pct=round(margin, 1),
            vs_current_revenue_pct=round((revenue - current_revenue) / current_revenue * 100, 1) if current_revenue else 0,
            vs_current_profit_pct=round((gross_profit - current_profit) / current_profit * 100, 1) if current_profit else 0,
        )

    # Break-even price
    break_even_price = cost  # minimum price to not lose money per unit
    break_even_units = demand_at(break_even_price)

    # Optimal price via calculus: p* = cost * e / (e + 1)  [markup rule for constant elasticity]
    if e < -1:
        optimal_price = cost * e / (e + 1)
        optimal_price = max(optimal_price, cost * 1.05)  # floor at 5% margin
    else:
        # Elasticity ≥ -1 means demand is inelastic; test a grid instead
        optimal_price = _grid_search_optimal(p0, q0, cost, e)

    optimal_scenario = make_scenario(optimal_price)

    # Generate scenarios: current price ±40% in 5% steps + optimal
    prices = sorted({
        round(p0 * factor, 2)
        for factor in [0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.4]
    } | {round(optimal_price, 2)})

    scenarios = [make_scenario(p) for p in prices if p > cost]
    current = make_scenario(p0)

    # Market position context
    market_position = None
    if data.market_median_price:
        diff_pct = (p0 - data.market_median_price) / data.market_median_price * 100
        if diff_pct > 15:
            market_position = f"You are {abs(diff_pct):.1f}% above market median (MYR {data.market_median_price:.2f})"
        elif diff_pct < -15:
            market_position = f"You are {abs(diff_pct):.1f}% below market median (MYR {data.market_median_price:.2f})"
        else:
            market_position = f"Your price is near market median (MYR {data.market_median_price:.2f})"

    recommendation = _build_recommendation(current, optimal_scenario, break_even_price)

    return ROIOutput(
        current=current,
        break_even_price=round(break_even_price, 2),
        break_even_units=round(break_even_units, 1),
        optimal_price=round(optimal_price, 2),
        optimal_revenue=optimal_scenario.revenue,
        optimal_margin_pct=optimal_scenario.margin_pct,
        scenarios=scenarios,
        recommendation=recommendation,
        market_position=market_position,
    )


def _grid_search_optimal(p0: float, q0: float, cost: float, e: float) -> float:
    best_profit, best_price = -1e9, p0
    for mult in [x / 100 for x in range(50, 301, 5)]:
        price = p0 * mult
        if price <= cost:
            continue
        units = q0 * math.pow(price / p0, e)
        profit = (price - cost) * units
        if profit > best_profit:
            best_profit = profit
            best_price = price
    return best_price


def _build_recommendation(current: PriceScenario, optimal: PriceScenario, break_even: float) -> str:
    if optimal.price > current.price:
        direction = "Raising"
        action = f"raise to MYR {optimal.price:.2f}"
    elif optimal.price < current.price:
        direction = "Lowering"
        action = f"lower to MYR {optimal.price:.2f}"
    else:
        return f"Your current price of MYR {current.price:.2f} is already near optimal."

    profit_delta = optimal.gross_profit - current.gross_profit
    sign = "+" if profit_delta >= 0 else ""
    return (
        f"{direction} your price to MYR {optimal.price:.2f} is estimated to "
        f"{sign}{profit_delta:.2f} MYR/month gross profit "
        f"({sign}{optimal.vs_current_profit_pct:.1f}% change). "
        f"Break-even is at MYR {break_even:.2f}. "
        f"Optimal margin: {optimal.margin_pct:.1f}%."
    )
