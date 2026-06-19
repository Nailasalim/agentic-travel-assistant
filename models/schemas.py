"""Pydantic schemas for structured agent outputs."""

from pydantic import BaseModel, Field, field_validator

from utils.coercion import coerce_int


class DayPlan(BaseModel):
    day: int
    title: str
    activities: list[str]
    meals: list[str]
    estimated_cost: int = Field(ge=0)

    @field_validator("day", "estimated_cost", mode="before")
    @classmethod
    def coerce_day_fields(cls, value):
        return coerce_int(value, 0)


class ItineraryPlan(BaseModel):
    destination: str
    total_days: int
    travelers: int = 1
    days: list[DayPlan]
    summary: str

    @field_validator("total_days", "travelers", mode="before")
    @classmethod
    def coerce_plan_ints(cls, value):
        return coerce_int(value, 1)


class HotelOption(BaseModel):
    name: str
    price_per_night: int = Field(ge=0)
    hotel_type: str
    reason: str
    fits_budget: bool
    total_stay_cost: int = Field(ge=0)
    is_recommended: bool = False

    @field_validator("price_per_night", "total_stay_cost", mode="before")
    @classmethod
    def coerce_hotel_ints(cls, value):
        return coerce_int(value, 0)


class HotelRecommendation(BaseModel):
    destination: str
    travelers: int
    rooms_needed: int
    preference_used: str
    recommendations: list[HotelOption]
    selected_hotel: str
    selected_hotel_total_cost: int
    summary: str

    @field_validator("travelers", "rooms_needed", "selected_hotel_total_cost", mode="before")
    @classmethod
    def coerce_hotel_rec_ints(cls, value):
        return coerce_int(value, 0)


class BudgetBreakdown(BaseModel):
    travelers: int
    rooms_required: int
    days: int
    total_budget: float
    selected_hotel_name: str
    hotel_nights: int
    hotel_total: float
    remaining_budget: float
    food: float
    transport: float
    activities: float
    total: float
    within_budget: bool
    per_person_estimate: float
    notes: str
    allocation_rationale: str

    @field_validator("travelers", "rooms_required", "days", "hotel_nights", mode="before")
    @classmethod
    def coerce_budget_ints(cls, value):
        return coerce_int(value, 0)


class PlaceItem(BaseModel):
    name: str
    description: str
    category: str


class PlaceRecommendations(BaseModel):
    destination: str
    restaurants: list[PlaceItem]
    attractions: list[PlaceItem]
    hidden_gems: list[PlaceItem]
    summary: str = ""


class TopExperience(BaseModel):
    title: str
    reason: str
    estimated_spend: int = Field(ge=0)
    preference_match: str

    @field_validator("estimated_spend", mode="before")
    @classmethod
    def coerce_spend(cls, value):
        return coerce_int(value, 0)


class TripRecommendations(BaseModel):
    destination: str
    travelers: int
    rooms_required: int = 1
    summary: str
    top_experiences: list[TopExperience]

    @field_validator("travelers", "rooms_required", mode="before")
    @classmethod
    def coerce_rec_ints(cls, value):
        return coerce_int(value, 1)
