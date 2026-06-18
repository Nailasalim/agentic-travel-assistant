from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

def planner_agent(state):

    destination = state["destination"]
    days = state["days"]
    budget = state["budget"]

    prompt = f"""
    Create a detailed {days}-day travel itinerary.

    Destination: {destination}
    Budget: ₹{budget}

    Include:
    - Attractions
    - Activities
    - Food recommendations

    Keep the itinerary concise.
    """

    response = llm.invoke(prompt)

    state["itinerary"] = response.content

    return state