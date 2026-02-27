import json
import re
from typing import List

import pandas as pd

from festy_crew.models.festival import EnrichedContact, Festival, FestivalList


def festivals_to_csv(crew_output, output_path: str) -> pd.DataFrame:
    """Convert ResearchCrew output to CSV. Tries pydantic first, falls back to parsing raw text."""
    festivals: List[Festival] = []

    # Try pydantic output first
    if hasattr(crew_output, "pydantic") and crew_output.pydantic is not None:
        pydantic_out = crew_output.pydantic
        if isinstance(pydantic_out, FestivalList):
            festivals = pydantic_out.festivals

    # Fall back to parsing raw output
    if not festivals and hasattr(crew_output, "raw") and crew_output.raw:
        festivals = _parse_raw_festivals(crew_output.raw)

    if not festivals:
        print("Warning: No festivals found in crew output. Creating empty CSV.")
        df = pd.DataFrame(
            columns=[
                "name", "country", "location", "dates", "genres", "website",
                "description", "genre_fit_score", "why_it_fits", "known_acts", "Approved",
            ]
        )
        df.to_csv(output_path, index=False)
        return df

    records = [f.model_dump() for f in festivals]
    df = pd.DataFrame(records)
    df["Approved"] = ""
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} festivals to {output_path}")
    return df


def _parse_raw_festivals(raw_text: str) -> List[Festival]:
    """Attempt to extract festival data from raw LLM text output."""
    festivals = []

    # Try JSON block extraction
    json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", raw_text)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, dict) and "festivals" in data:
                return FestivalList(**data).festivals
            if isinstance(data, list):
                return FestivalList(festivals=data).festivals
        except Exception:
            pass

    # Try bare JSON
    try:
        data = json.loads(raw_text.strip())
        if isinstance(data, dict) and "festivals" in data:
            return FestivalList(**data).festivals
    except Exception:
        pass

    return festivals


def load_approved_festivals(csv_path: str) -> List[dict]:
    """Load festivals from CSV where Approved column is 'Yes' (case-insensitive)."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return []

    if "Approved" not in df.columns:
        print(
            "Warning: 'Approved' column not found in CSV.\n"
            "Please add an 'Approved' column and mark entries with 'Yes' to include them in Phase 2."
        )
        return []

    approved = df[df["Approved"].str.strip().str.lower() == "yes"]
    records = approved.to_dict(orient="records")
    print(f"Loaded {len(records)} approved festivals from {csv_path}")
    return records


def enriched_to_csv(
    contacts: List[EnrichedContact], original_csv: str, output_path: str
) -> pd.DataFrame:
    """Merge enriched contact data with the original festival CSV and save."""
    try:
        original_df = pd.read_csv(original_csv)
    except FileNotFoundError:
        print(f"Warning: Original CSV not found at {original_csv}. Creating standalone output.")
        original_df = pd.DataFrame()

    contact_records = [c.model_dump() for c in contacts]
    contacts_df = pd.DataFrame(contact_records)

    if contacts_df.empty:
        print("No enriched contacts to save.")
        return contacts_df

    contacts_df = contacts_df.rename(
        columns={
            "festival_name": "name",
            "organizer_name": "Organizer Name",
            "emails": "Emails",
            "confidence": "Confidence",
            "source": "Source",
            "notes": "Notes",
        }
    )

    if not original_df.empty and "name" in original_df.columns:
        merged = original_df.merge(contacts_df, on="name", how="left")
    else:
        merged = contacts_df

    merged.to_csv(output_path, index=False)

    # Append disclaimer as a comment row
    with open(output_path, "a") as f:
        f.write(
            "\n# IMPORTANT: This data is provided for legitimate music industry outreach only. "
            "Comply with all applicable privacy laws (GDPR, CAN-SPAM, etc.) when contacting individuals. "
            "Verify all contact details before use."
        )

    print(f"Saved enriched data for {len(contacts)} festivals to {output_path}")
    return merged
