def budget_agent(state):

    total_budget = state["budget"]

    state["budget_breakdown"] = {
        "hotel": total_budget * 0.4,
        "food": total_budget * 0.2,
        "transport": total_budget * 0.2,
        "activities": total_budget * 0.2
    }

    return state