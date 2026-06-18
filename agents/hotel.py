from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data.hotels import HOTELS

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

def hotel_agent(state):

    budget = state["budget"]

    prompt = f"""
    You are a hotel recommendation expert.

    User budget: ₹{budget}

    Available hotels:

    {HOTELS}

    Recommend the best hotel options.

    Explain:
    - Why each hotel is suitable
    - Whether it fits the budget
    - Who it is best for

    Keep the answer concise.
    """

    response = llm.invoke(prompt)

    state["hotels"] = response.content

    return state