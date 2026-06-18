from graph.travel_graph import app

config = {
    "configurable": {
        "thread_id": "user_1"
    }
}

result1 = app.invoke(
    {
        "destination": "Goa",
        "days": 4,
        "budget": 30000,
        "preferences": {
            "hotel_type": "Beach Resort"
        }
    },
    config=config
)

print("FIRST RUN")
print(result1)

result2 = app.invoke(
    {
        "destination": "Goa",
        "days": 3,
        "budget": 25000
    },
    config=config
)

print("\nSECOND RUN")
print(result2)