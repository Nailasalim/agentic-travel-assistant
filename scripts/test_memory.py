import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from langgraph.types import Command

from graph.travel_graph import app

config = {
    "configurable": {
        "thread_id": "user_1"
    }
}

app.invoke(
    {
        "destination": "Goa",
        "days": 4,
        "budget": 30000,
        "travelers": 2,
        "rooms_required": 1,
        "preferences": {
            "hotel_type": "Beach Resort"
        }
    },
    config=config
)

app.invoke(Command(resume={"action": "approve", "feedback": ""}), config=config)
result1 = app.get_state(config).values

print("FIRST RUN")
print(result1)

app.invoke(
    {
        "destination": "Goa",
        "days": 3,
        "budget": 25000
    },
    config=config
)

app.invoke(Command(resume={"action": "approve", "feedback": ""}), config=config)
result2 = app.get_state(config).values

print("\nSECOND RUN")
print(result2)