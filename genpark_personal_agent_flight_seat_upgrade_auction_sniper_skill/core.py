# -*- coding: utf-8 -*-
"""Flight Seat Upgrade Auction Sniper Skill for GenPark Personal Travel Agents."""
import json
import math
from typing import Dict, Any

def calculate_optimal_upgrade_bid(economy_ticket_cost_usd: float, retail_business_ticket_cost_usd: float, minimum_allowable_bid_usd: float, unsold_premium_seats_count: int, maximum_allowable_bid_usd: float = 0.0, hours_prior_to_departure: int = 48) -> Dict[str, Any]:
    retail_delta_usd = max(0.0, retail_business_ticket_cost_usd - economy_ticket_cost_usd)
    
    # Seats scarcity multiplier
    if unsold_premium_seats_count >= 8:
        scarcity_factor = 0.25 # Aggressive low bid
        acceptance_prob = "HIGH (Plenty of empty premium inventory)"
    elif unsold_premium_seats_count >= 4:
        scarcity_factor = 0.45 # Sweet spot bid
        acceptance_prob = "MODERATE_BALANCED"
    elif unsold_premium_seats_count >= 1:
        scarcity_factor = 0.70 # High competition
        acceptance_prob = "COMPETITIVE_TIGHT"
    else:
        return {"status": "ZERO_AVAILABILITY", "recommended_bid_usd": 0.0, "reason": "No unsold premium seats left."}

    # Bid formula: Min bid + (Range * Scarcity Factor)
    if maximum_allowable_bid_usd > minimum_allowable_bid_usd:
        bid_range = maximum_allowable_bid_usd - minimum_allowable_bid_usd
        recommended_bid = round(minimum_allowable_bid_usd + (bid_range * scarcity_factor), 0)
    else:
        recommended_bid = round(max(minimum_allowable_bid_usd, retail_delta_usd * scarcity_factor), 0)

    # Sanity check: Ensure bid does not exceed 65% of retail delta
    bid_ceiling = retail_delta_usd * 0.65
    final_bid = min(recommended_bid, bid_ceiling) if bid_ceiling > 0 else recommended_bid

    discount_vs_retail = round(((retail_delta_usd - final_bid) / max(1.0, retail_delta_usd)) * 100, 1)

    return {
        "retail_spread_usd": round(retail_delta_usd, 2),
        "unsold_seats_available": unsold_premium_seats_count,
        "hours_to_departure": hours_prior_to_departure,
        "minimum_bid_usd": minimum_allowable_bid_usd,
        "recommended_optimal_bid_usd": final_bid,
        "discount_vs_full_fare_pct": discount_vs_retail,
        "predicted_acceptance_tier": acceptance_prob,
        "strategy": "Snipe bid at T-24h when airline yield algorithms lower clearance threshold."
    }

def audit_cabin_amenity_arbitrage_value(flight_duration_hours: float, bid_amount_usd: float, has_lounge_access: bool = True, extra_bags_count: int = 2) -> Dict[str, Any]:
    lounge_value = 65.0 if has_lounge_access else 0.0
    baggage_value = extra_bags_count * 45.0
    
    # Valuation of lie-flat sleep on long-haul (> 6 hours) is $35/hour
    comfort_value = round(flight_duration_hours * (40.0 if flight_duration_hours > 6.0 else 20.0), 2)
    total_hard_soft_value = lounge_value + baggage_value + comfort_value

    net_value_surplus = round(total_hard_soft_value - bid_amount_usd, 2)
    is_positive_roi = net_value_surplus > 0

    return {
        "flight_duration_hours": flight_duration_hours,
        "bid_cost_usd": bid_amount_usd,
        "lounge_perk_value_usd": lounge_value,
        "baggage_fee_waiver_value_usd": baggage_value,
        "sleep_comfort_valuation_usd": comfort_value,
        "total_amenity_valuation_usd": total_hard_soft_value,
        "net_arbitrage_surplus_usd": net_value_surplus,
        "is_value_accretive": is_positive_roi,
        "arbiter": "GenPark Travel Amenity Valuation Engine"
    }
