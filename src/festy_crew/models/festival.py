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


class FestivalList(BaseModel):
    festivals: List[Festival]


class EnrichedContact(BaseModel):
    festival_name: str
    organizer_name: str = "Not Found"
    emails: str = ""
    confidence: str = "Low"
    source: str = ""
    notes: str = ""
