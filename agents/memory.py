from memory.preferences import user_preferences
from utils.state_helpers import ensure_trip_defaults, reset_stale_trip_fields


def memory_agent(state):
    state = ensure_trip_defaults(state)
    state = reset_stale_trip_fields(state)

    thread_id = state.get("thread_id", "default_user")

    if state.get("preferences"):
        user_preferences[thread_id] = state["preferences"]
    elif thread_id in user_preferences:
        state["preferences"] = user_preferences[thread_id]
    else:
        state["preferences"] = {}

    return state
