"""Defensive parsing for LLM structured outputs."""


def coerce_int(value, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("₹", "")
        if not cleaned:
            return default
        return int(float(cleaned))
    return default


def coerce_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("₹", "")
        if not cleaned:
            return default
        return float(cleaned)
    return default
