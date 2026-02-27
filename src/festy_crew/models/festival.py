from typing import List
from pydantic import BaseModel


class Festival(BaseModel):
    name: str
    country: str
    location: str
    dates: str
    genres: str
    website: str
    description: str
    genre_fit_score: str  # "High" | "Medium" | "Low"
    why_it_fits: str
    known_acts: str
    submission_info: str = ""  # Open call details, application deadlines, or "Unknown"


class FestivalList(BaseModel):
    festivals: List[Festival]


class IndividualContact(BaseModel):
    name: str = ""
    role: str = ""   # e.g. "Booking Manager", "Festival Director", "Press"
    email: str = ""


class EnrichedContact(BaseModel):
    festival_name: str
    contacts: List[IndividualContact] = []
    confidence: str = "Low"
    source: str = ""
    notes: str = ""
