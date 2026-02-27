import concurrent.futures
import os
from crewai.tools import BaseTool
from pydantic import Field


def _scrape_with_timeout(app, url: str, timeout_seconds: int = 20):
    """Run a Firecrawl scrape with a hard timeout to prevent hangs."""
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(app.scrape, url, formats=["markdown"])
    try:
        result = future.result(timeout=timeout_seconds)
        executor.shutdown(wait=False)
        return result
    except concurrent.futures.TimeoutError:
        executor.shutdown(wait=False)
        return None


def _get_firecrawl_client():
    from firecrawl import FirecrawlApp
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable is not set")
    return FirecrawlApp(api_key=api_key)


class FirecrawlScrapeTool(BaseTool):
    name: str = "FirecrawlScrapeTool"
    description: str = (
        "Scrapes a webpage and returns its content as markdown. "
        "Use this to extract content from a specific URL. "
        "Input: url (str) - the full URL to scrape."
    )

    def _run(self, url: str) -> str:
        try:
            app = _get_firecrawl_client()
            result = _scrape_with_timeout(app, url)
            if result is None:
                return f"Timed out retrieving content from {url}"
            markdown = result.markdown or ""
            if not markdown:
                return f"No content retrieved from {url}"
            return markdown[:3000]
        except Exception as e:
            return f"Could not retrieve content from {url}: {e}"


class FirecrawlSearchTool(BaseTool):
    name: str = "FirecrawlSearchTool"
    description: str = (
        "Searches the web using Firecrawl and returns relevant results. "
        "Use this to discover festival websites and articles. "
        "Input: query (str) - the search query. Optionally: limit (int, default 5)."
    )
    limit: int = Field(default=5)

    def _run(self, query: str, limit: int = 5) -> str:
        try:
            app = _get_firecrawl_client()
            result = app.search(query, limit=limit)
            items = result.web or []
            if not items:
                return f"No results found for query: {query}"

            formatted = []
            for item in items:
                url = getattr(item, "url", "")
                title = getattr(item, "title", None) or "No title"
                description = getattr(item, "description", None) or ""
                formatted.append(f"URL: {url}\nTitle: {title}\nSnippet: {description}\n")
            return "\n".join(formatted)
        except Exception as e:
            return f"Search failed: {e}"


class WebsiteContactFinderTool(BaseTool):
    name: str = "WebsiteContactFinderTool"
    description: str = (
        "Crawls common contact-related pages on a festival website to find organizer contact info. "
        "Checks /contact, /about, /team, /press, /organizers, /submissions pages. "
        "Input: base_url (str) - the festival's base website URL (e.g. https://festival.com)."
    )

    def _run(self, base_url: str) -> str:
        app = _get_firecrawl_client()
        contact_paths = ["/contact", "/about", "/team", "/press", "/organizers", "/submissions"]
        base_url = base_url.rstrip("/")
        aggregated = []

        for path in contact_paths:
            url = f"{base_url}{path}"
            try:
                result = _scrape_with_timeout(app, url)
                if result is None:
                    continue
                markdown = result.markdown or ""
                if markdown and len(markdown) > 100:
                    aggregated.append(f"=== {url} ===\n{markdown[:1500]}")
            except Exception:
                continue

        if not aggregated:
            try:
                result = _scrape_with_timeout(app, base_url)
                if result is None:
                    return f"Timed out retrieving contact information from {base_url}"
                markdown = result.markdown or ""
                if markdown:
                    aggregated.append(f"=== {base_url} (homepage) ===\n{markdown[:2000]}")
            except Exception as e:
                return f"Could not retrieve any contact information from {base_url}: {e}"

        return "\n\n".join(aggregated) if aggregated else f"No contact information found at {base_url}"
