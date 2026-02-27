#!/usr/bin/env python3
"""
Phase 1: Discover indie-pop-aligned Asian music festivals.

Runs a two-agent CrewAI pipeline:
  1. festival_researcher — searches and scrapes for festival candidates
  2. genre_filter_analyst — scores and filters by indie alignment

Outputs: festivals_phase1.csv (with empty "Approved" column for user review)
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from festy_crew.research_crew.crew import ResearchCrew
from festy_crew.utils.csv_handler import festivals_to_csv


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║           festy-crew — Phase 1: Festival Discovery           ║
║     Finding indie-pop-aligned Asian music festivals 2026     ║
╚══════════════════════════════════════════════════════════════╝
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Discover indie-pop-aligned Asian music festivals for 2026"
    )
    parser.add_argument(
        "--output",
        default="festivals_phase1.csv",
        help="Output CSV file path (default: festivals_phase1.csv)",
    )
    return parser.parse_args()


def main():
    print(BANNER)
    args = parse_args()

    inputs = {
        "target_year": "2026",
        "regions": (
            "Asia (Japan, South Korea, Thailand, Philippines, Indonesia, Taiwan, "
            "India, Vietnam, Malaysia, Singapore, Hong Kong, China, and more)"
        ),
        "genre_focus": (
            "indie pop, dream pop, shoegaze, synth-pop, chillwave, indie folk, "
            "indie electronic, bedroom pop, indie rock, lo-fi"
        ),
    }

    print("Starting festival discovery...\n")
    print(f"Target year: {inputs['target_year']}")
    print(f"Regions: {inputs['regions']}")
    print(f"Genre focus: {inputs['genre_focus']}\n")
    print("=" * 64)

    try:
        result = ResearchCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        print(f"\nError running research crew: {e}")
        sys.exit(1)

    print("\n" + "=" * 64)
    print("Research complete. Saving results...")

    df = festivals_to_csv(result, args.output)

    print(f"\n{'=' * 64}")
    print(f"Results saved to: {args.output}")
    print(f"Total festivals found: {len(df)}")

    if not df.empty and "genre_fit_score" in df.columns:
        high = (df["genre_fit_score"].str.lower() == "high").sum()
        medium = (df["genre_fit_score"].str.lower() == "medium").sum()
        print(f"  High fit:   {high}")
        print(f"  Medium fit: {medium}")

    print(f"\n{'=' * 64}")
    print("NEXT STEPS:")
    print(f"  1. Open {args.output} in a spreadsheet editor")
    print("  2. Review each festival entry")
    print("  3. Add 'Approved' column with 'Yes' for festivals to enrich")
    print(f"  4. Run: python phase2.py {args.output}")
    print("=" * 64)


if __name__ == "__main__":
    main()
