import os
import time
from typing import Optional
import requests
from crewai.tools import BaseTool
from pydantic import Field


HUNTER_BASE_URL = "https://api.hunter.io/v2"


def _get_hunter_key() -> Optional[str]:
    return os.getenv("HUNTER_API_KEY") or None


class HunterDomainSearchTool(BaseTool):
    name: str = "HunterDomainSearchTool"
    description: str = (
        "Searches Hunter.io for email addresses associated with a domain. "
        "Use this to find festival organizer emails by their website domain. "
        "Input: domain (str) - the domain to search (e.g. 'festival.com'). "
        "Optionally: limit (int, default 10)."
    )
    limit: int = Field(default=10)

    def _run(self, domain: str, limit: int = 10) -> str:
        api_key = _get_hunter_key()
        if not api_key:
            return "HUNTER_API_KEY not configured — skipping Hunter domain lookup"

        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        try:
            resp = requests.get(
                f"{HUNTER_BASE_URL}/domain-search",
                params={"domain": domain, "limit": limit, "api_key": api_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            emails = data.get("emails", [])
            if not emails:
                return f"No emails found for domain: {domain}"

            lines = []
            for entry in emails:
                email = entry.get("value", "")
                confidence = entry.get("confidence", "")
                position = entry.get("position", "")
                first = entry.get("first_name", "")
                last = entry.get("last_name", "")
                name = f"{first} {last}".strip()
                lines.append(
                    f"Email: {email} | Confidence: {confidence}% | Name: {name} | Position: {position}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Hunter lookup failed: {e}"


class HunterEmailVerifierTool(BaseTool):
    name: str = "HunterEmailVerifierTool"
    description: str = (
        "Verifies whether an email address is valid using Hunter.io. "
        "Use this to confirm emails found during contact research. "
        "Input: email (str) - the email address to verify."
    )

    def _run(self, email: str) -> str:
        api_key = _get_hunter_key()
        if not api_key:
            return "HUNTER_API_KEY not configured — skipping email verification"

        time.sleep(1)  # rate limiting
        try:
            resp = requests.get(
                f"{HUNTER_BASE_URL}/email-verifier",
                params={"email": email, "api_key": api_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            status = data.get("status", "unknown")
            score = data.get("score", "")
            result = data.get("result", "")
            return f"Email: {email} | Status: {status} | Score: {score} | Result: {result}"
        except Exception as e:
            return f"Hunter verification failed: {e}"
