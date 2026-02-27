#!/usr/bin/env python3
"""
Phase 2: Enrich approved festivals with organizer contact information.

Reads approved festivals from Phase 1 CSV and runs a two-agent enrichment
pipeline for each:
  1. contact_finder — crawls festival website for contact info
  2. email_enricher — uses Hunter.io to find and verify emails

Outputs: festivals_phase2_enriched.csv
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from festy_crew.enrichment_crew.crew import EnrichmentCrew
from festy_crew.models.festival import EnrichedContact
from festy_crew.utils.csv_handler import enriched_to_csv, load_approved_festivals


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          festy-crew — Phase 2: Contact Enrichment            ║
║        Finding organizer emails for approved festivals       ║
╚══════════════════════════════════════════════════════════════╝
"""

DISCLAIMER = """
IMPORTANT: This tool is for legitimate music industry outreach only.
When contacting festival organizers, comply with all applicable privacy
laws including GDPR, CAN-SPAM Act, and local regulations. Always:
  - Include a clear unsubscribe option in your emails
  - Identify yourself and your organization honestly
  - Respect opt-out requests immediately
  - Only contact people with a legitimate business reason
"""


def main():
    print(BANNER)

    # Accept CSV path as first positional argument
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "festivals_phase1.csv"
    output_path = "festivals_phase2_enriched.csv"

    print(f"Loading approved festivals from: {csv_path}\n")
    approved = load_approved_festivals(csv_path)

    if not approved:
        print("No approved festivals found. Please add 'Yes' in the 'Approved' column.")
        sys.exit(0)

    print(f"Found {len(approved)} approved festivals to enrich.\n")
    print("=" * 64)

    results = []
    total = len(approved)

    for i, festival in enumerate(approved, 1):
        name = festival.get("name", f"Festival {i}")
        website = festival.get("website", "")

        print(f"\nProcessing festival {i}/{total}: {name}")
        print(f"  Website: {website}")
        print("-" * 40)

        if not website:
            print(f"  Warning: No website for {name}, skipping enrichment.")
            results.append(
                EnrichedContact(
                    festival_name=name,
                    notes="No website available for contact lookup",
                )
            )
            continue

        inputs = {
            "festival_name": name,
            "website": website,
            "country": festival.get("country", ""),
            "location": festival.get("location", ""),
        }

        try:
            crew_result = EnrichmentCrew().crew().kickoff(inputs=inputs)

            if hasattr(crew_result, "pydantic") and isinstance(crew_result.pydantic, EnrichedContact):
                contact = crew_result.pydantic
            else:
                contact = EnrichedContact(
                    festival_name=name,
                    notes=f"Could not parse structured output. Raw: {str(crew_result.raw)[:200]}",
                )
            results.append(contact)
            print(f"  Confidence: {contact.confidence} | Emails: {contact.emails or 'None found'}")

        except Exception as e:
            print(f"  Error enriching {name}: {e}")
            results.append(
                EnrichedContact(
                    festival_name=name,
                    notes=f"Enrichment failed: {str(e)[:200]}",
                )
            )

    print("\n" + "=" * 64)
    print(f"Enrichment complete. Saving results to {output_path}...")

    enriched_to_csv(results, csv_path, output_path)

    high = sum(1 for r in results if r.confidence == "High")
    medium = sum(1 for r in results if r.confidence == "Medium")
    low = sum(1 for r in results if r.confidence == "Low")

    print(f"\n{'=' * 64}")
    print(f"Results saved to: {output_path}")
    print(f"Total festivals processed: {total}")
    print(f"  High confidence contacts:   {high}")
    print(f"  Medium confidence contacts: {medium}")
    print(f"  Low confidence / not found: {low}")

    print(f"\n{DISCLAIMER}")
    print("=" * 64)


if __name__ == "__main__":
    main()
