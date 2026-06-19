"""
Streamlit frontend for the Travel Planning Assistant.

Requires the FastAPI backend running separately:
    uvicorn api.main:app --reload
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
import uuid
from typing import Any

import requests
import streamlit as st

from data.destinations import SUPPORTED_DESTINATIONS

DEFAULT_API_URL = os.getenv("TRAVEL_API_URL", "http://127.0.0.1:8000")

STAY_PREFERENCES = [
    "Any",
    "Beach Resort",
    "Budget",
    "Luxury",
    "Boutique",
    "Heritage",
]


def init_session_state() -> None:
    defaults = {
        "thread_id": None,
        "trip_status": "idle",
        "last_response": None,
        "approval_payload": None,
        "trip_result": None,
        "error_message": None,
        "selected_stay": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_post(path: str, payload: dict, api_url: str) -> dict[str, Any]:
    response = requests.post(f"{api_url}{path}", json=payload, timeout=300)
    if not response.ok:
        detail = response.text
        try:
            body = response.json()
            detail = body.get("detail", detail)
        except Exception:
            body = {}
        raise RuntimeError(f"API error ({response.status_code}): {detail}")
    return response.json()


def api_get(path: str, api_url: str) -> dict[str, Any]:
    response = requests.get(f"{api_url}{path}", timeout=60)
    if response.status_code == 404:
        raise RuntimeError("API error (404): Trip session not found")
    if not response.ok:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"API error ({response.status_code}): {detail}")
    return response.json()


def handle_stale_session(message: str) -> None:
    """Reset UI when backend no longer has this thread's checkpoint."""
    st.session_state.thread_id = None
    st.session_state.trip_status = "idle"
    st.session_state.approval_payload = None
    st.session_state.trip_result = None
    st.session_state.last_response = None
    st.session_state.selected_stay = None
    st.session_state.error_message = message


def sync_with_backend(api_url: str) -> None:
    """Align Streamlit session with backend checkpoint (survives page refresh)."""
    thread_id = st.session_state.thread_id
    if not thread_id:
        return

    try:
        data = api_get(f"/plan-trip/status/{thread_id}", api_url)
        _apply_response(data)
    except requests.exceptions.ConnectionError:
        return
    except RuntimeError as exc:
        if "404" in str(exc) or "not found" in str(exc).lower():
            handle_stale_session(
                "Your trip session expired. This usually happens after the server "
                "restarts. Please plan a new trip."
            )
        else:
            st.session_state.error_message = str(exc)


def start_trip(
    api_url: str,
    destination: str,
    days: int,
    budget: int,
    travelers: int,
    rooms_required: int,
    stay_preference: str,
) -> None:
    # Clear prior trip UI state before a new planning attempt
    st.session_state.trip_status = "idle"
    st.session_state.approval_payload = None
    st.session_state.trip_result = None
    st.session_state.error_message = None
    st.session_state.selected_stay = None
    st.session_state.last_response = None

    thread_id = f"streamlit_{uuid.uuid4().hex[:12]}"
    preferences = {}
    if stay_preference and stay_preference != "Any":
        preferences["hotel_type"] = stay_preference

    data = api_post(
        "/plan-trip",
        {
            "destination": destination,
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "rooms_required": rooms_required,
            "thread_id": thread_id,
            "preferences": preferences,
        },
        api_url,
    )

    st.session_state.thread_id = data.get("thread_id", thread_id)
    st.session_state.last_response = data
    st.session_state.error_message = None
    st.session_state.selected_stay = None
    _apply_response(data)


def resume_trip(api_url: str, action: str, feedback: str = "") -> None:
    if not st.session_state.thread_id:
        st.session_state.error_message = "No active trip. Start a new plan first."
        return

    try:
        data = api_post(
            "/plan-trip/resume",
            {
                "thread_id": st.session_state.thread_id,
                "action": action,
                "feedback": feedback,
            },
            api_url,
        )
    except RuntimeError as exc:
        msg = str(exc)
        if "No pending approval interrupt" in msg or "not found" in msg.lower():
            handle_stale_session(
                "Your approval session expired. This usually happens after the server "
                "restarts. Please plan a new trip below."
            )
        else:
            st.session_state.error_message = msg
        return

    st.session_state.last_response = data
    st.session_state.error_message = None
    _apply_response(data)


def select_stay(api_url: str, hotel_name: str) -> None:
    if not st.session_state.thread_id:
        st.session_state.error_message = "No active trip."
        return

    data = api_post(
        "/plan-trip/select-stay",
        {"thread_id": st.session_state.thread_id, "hotel_name": hotel_name},
        api_url,
    )

    st.session_state.selected_stay = hotel_name
    st.session_state.last_response = data
    st.session_state.error_message = None
    _apply_response(data)


def _apply_response(data: dict[str, Any]) -> None:
    status = data.get("status", "idle")
    st.session_state.trip_status = status

    if status != "error":
        st.session_state.error_message = None

    if status == "awaiting_approval":
        st.session_state.approval_payload = data.get("approval_payload")
        st.session_state.trip_result = data.get("state")
    elif status == "budget_infeasible":
        st.session_state.approval_payload = None
        st.session_state.trip_result = None
    elif status == "error":
        st.session_state.approval_payload = None
        st.session_state.trip_result = data.get("result") or data.get("state")
        if not data.get("message"):
            st.session_state.error_message = "Trip planning failed with an unknown error."
        else:
            st.session_state.error_message = data.get("message")
    elif status == "completed":
        st.session_state.approval_payload = None
        st.session_state.trip_result = data.get("result")
        hotels = (st.session_state.trip_result or {}).get("hotels", {})
        st.session_state.selected_stay = hotels.get("selected_hotel")
    elif status == "rejected":
        st.session_state.approval_payload = None
        st.session_state.trip_result = data.get("state")
    else:
        st.session_state.approval_payload = None
        st.session_state.trip_result = None


def reset_trip() -> None:
    st.session_state.thread_id = None
    st.session_state.trip_status = "idle"
    st.session_state.last_response = None
    st.session_state.approval_payload = None
    st.session_state.trip_result = None
    st.session_state.error_message = None
    st.session_state.selected_stay = None


def render_itinerary_structured(itinerary: dict | str | None) -> None:
    if not itinerary:
        st.write("_No itinerary yet._")
        return
    if isinstance(itinerary, str):
        st.markdown(itinerary)
        return

    travelers = itinerary.get("travelers")
    if travelers and travelers > 1:
        st.caption(f"Planned for **{travelers}** travelers")

    if itinerary.get("summary"):
        st.info(itinerary["summary"])

    for day in itinerary.get("days", []):
        with st.expander(f"Day {day.get('day')}: {day.get('title', 'Plan')}", expanded=True):
            st.caption(f"Estimated cost: ₹{day.get('estimated_cost', 0):,}")
            st.markdown("**Activities**")
            for activity in day.get("activities", []):
                st.markdown(f"- {activity}")
            st.markdown("**Meals**")
            for meal in day.get("meals", []):
                st.markdown(f"- {meal}")


def render_stay_structured(
    hotels: dict | str | None,
    days: int = 0,
    rooms_required: int = 1,
    api_url: str | None = None,
    allow_select: bool = False,
) -> None:
    if not hotels:
        st.write("_No stay options yet._")
        return
    if isinstance(hotels, str):
        st.markdown(hotels)
        return

    travelers = hotels.get("travelers", 1)
    rooms = hotels.get("rooms_needed", rooms_required)
    st.caption(f"**{travelers}** travelers · **{rooms}** room(s) required")

    if hotels.get("summary"):
        st.info(hotels["summary"])

    labels = ["Recommended Stay", "Alternative Stay 1", "Alternative Stay 2"]
    selected_name = hotels.get("selected_hotel", "")

    for idx, stay in enumerate(hotels.get("recommendations", [])[:3]):
        is_selected = stay.get("name") == selected_name or (
            stay.get("is_recommended") and not selected_name
        )
        label = labels[idx] if idx < len(labels) else f"Option {idx + 1}"
        budget_label = "Yes" if stay.get("fits_budget") else "No"
        total_cost = stay.get("total_stay_cost", 0)

        with st.container(border=True):
            st.markdown(f"**{label}**" + (" ✓ Selected" if is_selected else ""))
            st.markdown(f"**{stay.get('name')}** · {stay.get('hotel_type')}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Per night", f"₹{stay.get('price_per_night', 0):,}")
            col2.metric("Total stay cost", f"₹{total_cost:,}")
            col3.metric("Fits budget", budget_label)
            st.caption(stay.get("reason", ""))

            if allow_select and api_url and stay.get("name") != selected_name:
                if st.button(
                    "Select This Stay",
                    key=f"select_stay_{stay.get('name')}_{idx}",
                    use_container_width=True,
                ):
                    with st.spinner("Updating stay and budget..."):
                        try:
                            select_stay(api_url, stay.get("name"))
                        except Exception as exc:
                            st.session_state.error_message = str(exc)
                    st.rerun()


def render_places_structured(places: dict | None) -> None:
    if not places:
        st.write("_No places discovered yet._")
        return

    st.markdown("Explore what's available at your destination.")
    if places.get("summary"):
        st.caption(places["summary"])

    for label, key in [
        ("Restaurants", "restaurants"),
        ("Attractions", "attractions"),
        ("Hidden Gems", "hidden_gems"),
    ]:
        st.markdown(f"#### {label}")
        for item in places.get(key, []):
            st.markdown(f"**{item.get('name')}**")
            st.caption(item.get("description", ""))


def render_recommendations_structured(
    recommendations: dict | str | None, rooms_required: int = 1
) -> None:
    if not recommendations:
        st.write("_No personalized recommendations yet._")
        return
    if isinstance(recommendations, str):
        st.markdown(recommendations)
        return

    st.markdown("**What you should prioritize on this trip**")
    if recommendations.get("summary"):
        st.success(recommendations["summary"])

    travelers = recommendations.get("travelers")
    rooms = recommendations.get("rooms_required", rooms_required)
    st.caption(f"For **{travelers}** travelers · **{rooms}** room(s)")

    for idx, exp in enumerate(recommendations.get("top_experiences", []), start=1):
        with st.container(border=True):
            st.markdown(f"**{idx}. {exp.get('title')}**")
            st.markdown(f"₹{exp.get('estimated_spend', 0):,} estimated for your group")
            st.markdown(f"**Why:** {exp.get('reason', '')}")
            st.markdown(f"**Preference match:** {exp.get('preference_match', '')}")


def render_budget_structured(budget: dict | None) -> None:
    if not budget:
        st.write("_No budget breakdown yet._")
        return

    travelers = budget.get("travelers", 1)
    rooms = budget.get("rooms_required", 1)
    st.markdown(
        f"**{travelers}** travelers · **{rooms}** room(s) · **{budget.get('days', 0)}** days"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total trip budget", f"₹{budget.get('total_budget', 0):,.0f}")
        st.metric("Selected stay", budget.get("selected_hotel_name", "—"))
    with col2:
        st.metric(
            "Stay cost",
            f"₹{budget.get('hotel_total', 0):,.0f}",
            help=f"{budget.get('hotel_nights', 0)} nights",
        )
        st.metric("Remaining budget", f"₹{budget.get('remaining_budget', 0):,.0f}")

    st.markdown("#### Remaining allocation")
    cols = st.columns(3)
    cols[0].metric("Food", f"₹{budget.get('food', 0):,.0f}")
    cols[1].metric("Transport", f"₹{budget.get('transport', 0):,.0f}")
    cols[2].metric("Activities", f"₹{budget.get('activities', 0):,.0f}")

    st.metric("Per person (overall)", f"₹{budget.get('per_person_estimate', 0):,.0f}")

    if budget.get("allocation_rationale"):
        st.info(budget["allocation_rationale"])


def render_developer_tools(result: dict) -> None:
    with st.expander("Developer Tools", expanded=False):
        prefs = result.get("preferences") or {}
        if prefs:
            st.markdown("**Traveler Preferences**")
            st.json(prefs)
        st.markdown("**Structured trip data**")
        st.json(result)
        if st.session_state.thread_id:
            st.code(f"thread_id: {st.session_state.thread_id}")


def render_header() -> None:
    st.title("✈️ Travel Planning Assistant")
    st.caption("Plan your India trip — review your itinerary before we finalize stays and activities.")


def render_sidebar(api_url: str) -> str:
    with st.sidebar:
        st.header("Your trip")
        if st.session_state.trip_status != "idle":
            st.text_input("Status", value=st.session_state.trip_status, disabled=True)
        if st.button("Plan a new trip", use_container_width=True):
            reset_trip()
            st.rerun()
        st.divider()
        st.markdown("**Popular destinations**")
        st.write(", ".join(SUPPORTED_DESTINATIONS))
        with st.expander("Developer Tools", expanded=False):
            st.text_input("API URL", value=api_url, key="dev_api_url")
            st.text_input("Thread ID", value=st.session_state.thread_id or "—", disabled=True)
    return st.session_state.get("dev_api_url", api_url)


def render_trip_form(api_url: str) -> None:
    st.subheader("Where would you like to go?")
    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input(
            "Destination",
            value="Goa",
            placeholder="Type a city: Goa, Jaipur, Varkala...",
            help=f"Popular: {', '.join(SUPPORTED_DESTINATIONS)}",
        ).strip()
        days = st.number_input("Number of days", min_value=1, max_value=30, value=4, step=1)
        travelers = st.number_input(
            "People travelling",
            min_value=1,
            max_value=20,
            value=2,
            help="Total group size. Budget is for the entire group.",
        )
        rooms_required = st.number_input(
            "Rooms required",
            min_value=1,
            max_value=10,
            value=1,
            help="Number of rooms to book (you choose — not auto-calculated).",
        )

    with col2:
        budget = st.number_input(
            "Total trip budget (INR)",
            min_value=1000,
            max_value=5_000_000,
            value=30000,
            step=1000,
            help="Total budget for everyone travelling, not per person.",
        )
        stay_preference = st.selectbox("Stay preference", STAY_PREFERENCES, index=1)
        if travelers > 0 and budget > 0:
            st.caption(f"≈ ₹{budget // travelers:,} per person")

    if st.button("Plan my trip", type="primary", use_container_width=True):
        if not destination:
            st.session_state.error_message = "Please enter a destination."
            return
        with st.spinner("Discovering places and checking your budget..."):
            try:
                start_trip(
                    api_url=api_url,
                    destination=destination,
                    days=int(days),
                    budget=int(budget),
                    travelers=int(travelers),
                    rooms_required=int(rooms_required),
                    stay_preference=stay_preference,
                )
            except requests.exceptions.ConnectionError:
                st.session_state.error_message = "Cannot reach the planning service."
            except Exception as exc:
                st.session_state.error_message = str(exc)


def render_trip_summary_card(summary: dict) -> None:
    if not summary:
        return

    st.markdown("#### Trip Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Destination", summary.get("destination", "—"))
    c2.metric("Travelers", summary.get("travelers", "—"))
    c3.metric("Rooms required", summary.get("rooms_required", "—"))
    c4.metric("Days", summary.get("days", "—"))

    c5, c6, c7 = st.columns(3)
    c5.metric("Total budget", f"₹{summary.get('budget', 0):,}")
    c6.metric(
        "Stay preference",
        summary.get("stay_preference", summary.get("hotel_preference", "Any")),
    )
    c7.metric(
        "Est. stay cost",
        f"₹{summary.get('estimated_stay_cost', summary.get('estimated_hotel_cost', 0)):,}",
    )


def render_budget_infeasible() -> None:
    last = st.session_state.last_response or {}
    budget_error = last.get("budget_error") or {}

    st.divider()
    st.error("Your budget is too low for this trip configuration.")

    if budget_error:
        col1, col2 = st.columns(2)
        col1.metric("Your budget", f"₹{budget_error.get('user_budget', 0):,}")
        col2.metric(
            "Minimum needed",
            f"₹{budget_error.get('minimum_feasible_budget', 0):,}",
        )
        st.warning(f"Shortfall: ₹{budget_error.get('budget_shortfall', 0):,}")

        st.markdown("**Cost breakdown (minimum)**")
        b1, b2, b3 = st.columns(3)
        b1.metric("Stay", f"₹{budget_error.get('minimum_stay_cost', 0):,}")
        b2.metric("Food", f"₹{budget_error.get('minimum_food_cost', 0):,}")
        b3.metric("Transport", f"₹{budget_error.get('minimum_transport_cost', 0):,}")

        st.markdown("**Suggestions**")
        for tip in budget_error.get("suggestions", []):
            st.markdown(f"- {tip}")


def render_approval_section(api_url: str) -> None:
    payload = st.session_state.approval_payload
    if not payload:
        return

    st.divider()
    st.subheader("Review your itinerary")
    st.info(payload.get("message", "Please review your trip before continuing."))

    summary = payload.get("trip_summary") or {
        "destination": payload.get("destination"),
        "travelers": payload.get("travelers"),
        "rooms_required": payload.get("rooms_required"),
        "days": payload.get("days"),
        "budget": payload.get("budget"),
        "stay_preference": payload.get("stay_preference", payload.get("hotel_preference")),
        "estimated_stay_cost": payload.get(
            "estimated_stay_cost", payload.get("estimated_hotel_cost")
        ),
    }
    render_trip_summary_card(summary)

    st.markdown("#### Proposed itinerary")
    itinerary_plan = payload.get("itinerary_plan") or payload.get("itinerary")
    if isinstance(itinerary_plan, dict):
        render_itinerary_structured(itinerary_plan)
    else:
        st.markdown(payload.get("itinerary", "_No itinerary available._"))

    feedback = st.text_area(
        "What would you like to change?",
        placeholder="e.g. Add more beach time on Day 2.",
        height=100,
        key="modification_feedback",
    )

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("Approve itinerary", type="primary", use_container_width=True):
            with st.spinner("Finding stays and finalizing your plan..."):
                resume_trip(api_url, action="approve")
            st.rerun()
    with btn_col2:
        if st.button("Reject plan", use_container_width=True):
            with st.spinner("Stopping..."):
                resume_trip(api_url, action="reject")
            st.rerun()
    with btn_col3:
        if st.button("Request changes", use_container_width=True):
            if not feedback.strip():
                st.session_state.error_message = "Please describe what you'd like changed."
                st.rerun()
            with st.spinner("Updating your itinerary..."):
                resume_trip(api_url, action="modify", feedback=feedback.strip())
            st.rerun()


def render_rejected() -> None:
    result = st.session_state.trip_result or {}
    st.divider()
    st.error(result.get("approval_message", "Trip planning was stopped."))
    if result.get("itinerary"):
        with st.expander("Itinerary you reviewed"):
            render_itinerary_structured(result["itinerary"])


def render_completed_results(api_url: str) -> None:
    result = st.session_state.trip_result
    if not result:
        return

    st.divider()
    st.success("Your trip plan is ready!")

    cols = st.columns(5)
    cols[0].metric("Destination", result.get("destination", "—"))
    cols[1].metric("Travelers", result.get("travelers", 1))
    cols[2].metric("Rooms", result.get("rooms_required", 1))
    cols[3].metric("Days", result.get("days", "—"))
    cols[4].metric("Budget", f"₹{result.get('budget', 0):,}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Itinerary", "Stay", "Places", "Budget", "Recommendations"]
    )

    with tab1:
        render_itinerary_structured(result.get("itinerary"))
    with tab2:
        render_stay_structured(
            result.get("hotels"),
            days=result.get("days", 0),
            rooms_required=result.get("rooms_required", 1),
            api_url=api_url,
            allow_select=True,
        )
    with tab3:
        render_places_structured(result.get("places"))
    with tab4:
        render_budget_structured(result.get("budget_breakdown"))
    with tab5:
        render_recommendations_structured(
            result.get("recommendations"),
            rooms_required=result.get("rooms_required", 1),
        )

    render_developer_tools(result)


def main() -> None:
    st.set_page_config(page_title="Travel Planning Assistant", page_icon="✈️", layout="wide")
    init_session_state()
    render_header()
    api_url = render_sidebar(DEFAULT_API_URL)

    # Reconcile UI with backend (handles refresh + server restart)
    if st.session_state.thread_id:
        sync_with_backend(api_url)

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    render_trip_form(api_url)

    status = st.session_state.trip_status
    if status == "awaiting_approval":
        render_approval_section(api_url)
    elif status == "budget_infeasible":
        render_budget_infeasible()
    elif status == "rejected":
        render_rejected()
    elif status == "completed":
        render_completed_results(api_url)


if __name__ == "__main__":
    main()
