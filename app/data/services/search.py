import logging
import os
import requests
import wikipediaapi
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from tavily import TavilyClient

from .schemas import (
    ClaimNormalization,
    Evidence,
)

logger = logging.getLogger(__name__)

HTTP_USER_AGENT = (
    "FactCheckerApp/1.0 (https://github.com/spider-lilly/TruChat) Mozilla/5.0"
)

wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent=HTTP_USER_AGENT,
)


def _get_tavily_client():
    """Retrieve Tavily client if API key is configured."""
    api_key = getattr(settings, "TAVILY_API_KEY", None) or os.getenv("TAVILY_API_KEY")
    if not api_key or api_key.startswith("replace-with"):
        return None
    return TavilyClient(api_key=api_key)


def _search_gdelt(query: str) -> list[Evidence]:
    """Search GDELT DOC API and return Evidence objects."""
    try:
        url = settings.GDELT_BASE_URL
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": settings.SEARCH_RESULTS_PER_SOURCE,
        }
        headers = {"User-Agent": HTTP_USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.warning("GDELT search returned status %s", response.status_code)
            return []

        data = response.json()
        evidence = []

        for article in data.get("articles", []):
            evidence.append(
                Evidence(
                    source="GDELT",
                    url=article.get("url", ""),
                    title=article.get("title", ""),
                    raw_text=article.get("seendate", "") + "\n\n" + article.get("socialimage", ""),
                    text=article.get("seendate", "") + "\n\n" + article.get("socialimage", ""),
                    cleaned="",
                )
            )

        return evidence
    except Exception as e:
        logger.warning("GDELT search failed: %s", e)
        return []


def _search_wikipedia(query: str) -> list[Evidence]:
    """Search Wikipedia using the MediaWiki API and return Evidence objects."""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": settings.WIKIPEDIA_RESULTS,
        }
        headers = {"User-Agent": HTTP_USER_AGENT}
        response = requests.get(search_url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.warning("Wikipedia API returned status %s", response.status_code)
            return []

        data = response.json()
        evidence = []

        for result in data.get("query", {}).get("search", []):
            title = result.get("title")
            if not title:
                continue

            try:
                page = wiki.page(title)
                if not page.exists():
                    continue

                evidence.append(
                    Evidence(
                        source="Wikipedia",
                        url=page.fullurl,
                        title=page.title,
                        raw_text=page.text,
                        text=page.text,
                        cleaned="",
                    )
                )
            except Exception as e:
                logger.warning("Failed to fetch Wikipedia page '%s': %s", title, e)

        return evidence
    except Exception as e:
        logger.warning("Wikipedia search failed: %s", e)
        return []


def _search_wikidata(query: str) -> list[Evidence]:
    """Search Wikidata entities and return them as Evidence objects."""
    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": query,
            "limit": 5,
        }
        headers = {"User-Agent": HTTP_USER_AGENT}
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.warning("Wikidata search returned status %s", response.status_code)
            return []

        data = response.json()
        evidence = []

        for result in data.get("search", []):
            evidence.append(
                Evidence(
                    source="Wikidata",
                    url=f"https://www.wikidata.org/wiki/{result.get('id','')}",
                    title=result.get("label", ""),
                    raw_text=result.get("description", ""),
                    text=result.get("description", ""),
                    cleaned="",
                )
            )

        return evidence
    except Exception as e:
        logger.warning("Wikidata search failed: %s", e)
        return []


def _search_tavily(query: str) -> list[Evidence]:
    """Search Tavily and convert the response into Evidence objects."""
    try:
        tavily_client = _get_tavily_client()
        if not tavily_client:
            logger.warning("Tavily API key unconfigured, skipping Tavily search.")
            return []

        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_answer=False,
            include_raw_content=True,
        )

        evidence = []
        for result in response.get("results", []):
            evidence.append(
                Evidence(
                    source="Tavily",
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    raw_text=result.get("content", "") or result.get("raw_content", ""),
                    text=result.get("content", "") or result.get("raw_content", ""),
                    cleaned="",
                )
            )

        return evidence
    except Exception as e:
        logger.warning("Tavily search failed: %s", e)
        return []


def search_claim(claim: ClaimNormalization) -> list[Evidence]:
    """
    Search all configured sources concurrently and return a unified list of
    Evidence objects.
    """
    evidence = []

    with ThreadPoolExecutor(max_workers=settings.SEARCH_WORKERS) as executor:
        futures = {
            "tavily": executor.submit(_search_tavily, claim.search_queries.tavily),
            "wikipedia": executor.submit(_search_wikipedia, claim.search_queries.wikipedia),
            "wikidata": executor.submit(_search_wikidata, claim.search_queries.wikidata),
            "gdelt": executor.submit(_search_gdelt, claim.search_queries.gdelt),
        }

        for name, future in futures.items():
            try:
                res = future.result()
                if res:
                    evidence.extend(res)
            except Exception as e:
                logger.warning("Search provider '%s' failed: %s", name, e)

    return evidence
