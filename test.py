from graph.travel_graph import app

result = app.invoke(
    {
        "destination": "Goa",
        "days": 4,
        "budget": 30000
    }
)

print(result)