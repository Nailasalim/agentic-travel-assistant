from langgraph.graph import StateGraph, END

from graph.state import TravelState

from agents.planner import planner_agent
from agents.hotel import hotel_agent
from agents.budget import budget_agent
from agents.memory import memory_agent

from memory.store import memory

workflow = StateGraph(TravelState)

workflow.add_node("planner", planner_agent)
workflow.add_node("hotel", hotel_agent)
workflow.add_node("budget", budget_agent)
workflow.add_node("memory", memory_agent)

workflow.set_entry_point("memory")

workflow.add_edge("memory", "planner")
workflow.add_edge("planner", "hotel")
workflow.add_edge("hotel", "budget")
workflow.add_edge("budget", END)

app = workflow.compile(
    checkpointer=memory
)