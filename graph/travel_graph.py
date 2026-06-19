from langgraph.graph import StateGraph, END

from graph.state import TravelState

from agents.planner import planner_agent
from agents.hotel import hotel_agent
from agents.places import places_agent
from agents.budget import budget_agent
from agents.budget_validation import budget_validation_agent
from agents.memory import memory_agent
from agents.recommendation import recommendation_agent
from agents.approval import approval_agent

from memory.store import memory


def route_after_approval(state):
    status = state.get("approval_status", "rejected")

    if status == "approved":
        return "hotel"
    if status == "modification_requested":
        return "planner"

    return END


def route_after_budget_validation(state):
    if state.get("budget_feasible", True):
        return "planner"
    return END


workflow = StateGraph(TravelState)

workflow.add_node("planner", planner_agent)
workflow.add_node("approval", approval_agent)
workflow.add_node("hotel", hotel_agent)
workflow.add_node("places", places_agent)
workflow.add_node("budget_validation", budget_validation_agent)
workflow.add_node("budget", budget_agent)
workflow.add_node("memory", memory_agent)
workflow.add_node("recommendation", recommendation_agent)

workflow.set_entry_point("memory")

workflow.add_edge("memory", "places")
workflow.add_edge("places", "budget_validation")
workflow.add_conditional_edges("budget_validation", route_after_budget_validation)
workflow.add_edge("planner", "approval")
workflow.add_conditional_edges("approval", route_after_approval)
workflow.add_edge("hotel", "budget")
workflow.add_edge("budget", "recommendation")
workflow.add_edge("recommendation", END)

app = workflow.compile(checkpointer=memory)
