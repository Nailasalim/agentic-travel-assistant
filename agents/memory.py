def memory_agent(state):

    if "preferences" not in state:
        state["preferences"] = {}

    return state