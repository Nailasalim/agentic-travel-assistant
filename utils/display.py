"""Helpers for displaying structured state in HITL and UI."""

from models.schemas import (
    BudgetBreakdown,
    HotelRecommendation,
    ItineraryPlan,
    PlaceRecommendations,
    TripRecommendations,
)


def format_itinerary_for_display(itinerary) -> str:
    if itinerary is None:
        return ""

    if isinstance(itinerary, str):
        return itinerary

    if isinstance(itinerary, dict):
        try:
            plan = ItineraryPlan.model_validate(itinerary)
        except Exception:
            return itinerary.get("summary", str(itinerary))

        lines = [plan.summary, ""]
        if plan.travelers > 1:
            lines.append(f"Planned for {plan.travelers} travelers.")
            lines.append("")
        for day in plan.days:
            lines.append(f"**Day {day.day}: {day.title}** (est. ₹{day.estimated_cost:,})")
            lines.append("Activities:")
            lines.extend(f"- {item}" for item in day.activities)
            lines.append("Meals:")
            lines.extend(f"- {item}" for item in day.meals)
            lines.append("")
        return "\n".join(lines)

    return str(itinerary)


def format_hotels_for_display(hotels) -> str:
    if hotels is None:
        return ""

    if isinstance(hotels, str):
        return hotels

    if isinstance(hotels, dict):
        try:
            rec = HotelRecommendation.model_validate(hotels)
        except Exception:
            return hotels.get("summary", str(hotels))

        lines = [rec.summary, ""]
        for hotel in rec.recommendations:
            label = "Recommended" if hotel.is_recommended else "Alternative"
            budget_flag = "fits budget" if hotel.fits_budget else "over budget"
            lines.append(
                f"- **{hotel.name}** [{label}] ({hotel.hotel_type}) — "
                f"₹{hotel.price_per_night:,}/night, "
                f"₹{hotel.total_stay_cost:,} total — {budget_flag}"
            )
            lines.append(f"  {hotel.reason}")
        return "\n".join(lines)

    return str(hotels)


def format_recommendations_for_display(recommendations) -> str:
    if isinstance(recommendations, str):
        return recommendations

    if isinstance(recommendations, dict):
        try:
            trip_recs = TripRecommendations.model_validate(recommendations)
        except Exception:
            return recommendations.get("summary", str(recommendations))

        lines = []
        if trip_recs.summary:
            lines.append(trip_recs.summary)
            lines.append("")

        for idx, exp in enumerate(trip_recs.top_experiences, start=1):
            lines.append(f"{idx}. **{exp.title}** (est. ₹{exp.estimated_spend:,})")
            lines.append(f"   Reason: {exp.reason}")
            lines.append(f"   Preference match: {exp.preference_match}")
            lines.append("")

        return "\n".join(lines)

    return str(recommendations)


def format_places_for_display(places) -> str:
    if isinstance(places, str):
        return places

    if isinstance(places, dict):
        try:
            data = PlaceRecommendations.model_validate(places)
        except Exception:
            return places.get("summary", str(places))

        lines = []
        if data.summary:
            lines.append(data.summary)
            lines.append("")

        for label, items in [
            ("Restaurants", data.restaurants),
            ("Attractions", data.attractions),
            ("Hidden gems", data.hidden_gems),
        ]:
            lines.append(f"**{label}**")
            for item in items:
                lines.append(f"- **{item.name}**: {item.description}")
            lines.append("")

        return "\n".join(lines)

    return str(places)


def format_budget_for_display(budget) -> dict:
    if isinstance(budget, dict) and "total_budget" in budget:
        return budget

    if isinstance(budget, dict):
        try:
            breakdown = BudgetBreakdown.model_validate(budget)
            return breakdown.model_dump()
        except Exception:
            return budget

    return {}
