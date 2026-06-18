from fastapi import FastAPI
from pydantic import BaseModel

from graph.travel_graph import app as travel_app

app = FastAPI()


class TripRequest(BaseModel):
    destination: str
    days: int
    budget: int


@app.post("/plan-trip")
def plan_trip(request: TripRequest):

    result = travel_app.invoke(
    {
        "destination": request.destination,
        "days": request.days,
        "budget": request.budget,
        "preferences": {}
    },
    config={
        "configurable": {
            "thread_id": "user_1"
        }
    }
)

    return result