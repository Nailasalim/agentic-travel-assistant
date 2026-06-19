from langgraph.types import Command

from graph.travel_graph import app

config = {"configurable": {"thread_id": "user_1"}}

print("=== FIRST REQUEST ===")

app.invoke(
    {
        "thread_id": "user_1",
        "destination": "Goa",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
        "preferences": {
            "hotel_type": "Beach Resort"
        }
    },
    config=config,
)

snapshot = app.get_state(config)
print("\nAWAITING APPROVAL:", bool(snapshot.interrupts))

app.invoke(Command(resume={"action": "approve", "feedback": ""}), config=config)
result1 = app.get_state(config).values

print("\nHOTEL RECOMMENDATION:")
hotels1 = result1.get("hotels", {})
print(hotels1.get("summary", hotels1) if isinstance(hotels1, dict) else hotels1)

print("\nPREFERENCES:")
print(result1["preferences"])

print("\n\n=== SECOND REQUEST ===")

app.invoke(
    {
        "thread_id": "user_1",
        "destination": "Goa",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
    },
    config=config,
)

snapshot = app.get_state(config)
print("\nAWAITING APPROVAL:", bool(snapshot.interrupts))

app.invoke(Command(resume={"action": "approve", "feedback": ""}), config=config)
result2 = app.get_state(config).values

print("\nHOTEL RECOMMENDATION:")
hotels2 = result2.get("hotels", {})
print(hotels2.get("summary", hotels2) if isinstance(hotels2, dict) else hotels2)

print("\nPREFERENCES:")
print(result2["preferences"])