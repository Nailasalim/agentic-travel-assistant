"""Structured LLM output helpers with coercion and retry."""

from models.schemas import TripRecommendations
from utils.coercion import coerce_int


STRICT_SUFFIX = """
IMPORTANT — output schema rules:
- travelers must be an integer (e.g. 2), never a string
- estimated_spend must be an integer in INR (e.g. 800), never a string
- Return exactly 4 ranked top_experiences
"""


def normalize_trip_recommendations(data: dict, destination: str, travelers: int) -> dict:
    """Coerce numeric strings before Pydantic validation."""
    normalized = {
        "destination": destination,
        "travelers": coerce_int(data.get("travelers"), travelers),
        "summary": str(data.get("summary", "")),
        "top_experiences": [],
    }

    for item in data.get("top_experiences", []):
        normalized["top_experiences"].append(
            {
                "title": str(item.get("title", "Experience")),
                "reason": str(item.get("reason", "")),
                "estimated_spend": coerce_int(item.get("estimated_spend"), 0),
                "preference_match": str(item.get("preference_match", "")),
            }
        )

    model = TripRecommendations.model_validate(normalized)
    model.destination = destination
    model.travelers = travelers
    return model.model_dump()


def fallback_trip_recommendations(destination: str, travelers: int) -> dict:
    return TripRecommendations(
        destination=destination,
        travelers=travelers,
        summary=(
            f"Personalized highlights for {travelers} travelers in {destination}. "
            "Detailed ranking is temporarily unavailable."
        ),
        top_experiences=[],
    ).model_dump()


def invoke_trip_recommendations(llm, prompt: str, destination: str, travelers: int) -> dict:
    """Invoke structured recommendations with retry and graceful fallback."""
    structured_llm = llm.with_structured_output(TripRecommendations)

    for attempt, suffix in enumerate(["", STRICT_SUFFIX]):
        try:
            full_prompt = prompt if attempt == 0 else prompt + suffix
            raw = structured_llm.invoke(full_prompt)
            if hasattr(raw, "model_dump"):
                raw = raw.model_dump()
            return normalize_trip_recommendations(raw, destination, travelers)
        except Exception:
            if attempt == 1:
                return fallback_trip_recommendations(destination, travelers)

    return fallback_trip_recommendations(destination, travelers)
