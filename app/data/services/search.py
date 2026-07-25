import requests
from .schemas import (
    ClaimNormalization,
    Evidence,
)
import wikipediaapi
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from tavily import TavilyClient

tavily_client = TavilyClient(settings.TAVILY_API_KEY)

wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="FactChecker/1.0 "
)


def _search_gdelt(query: str) -> list[Evidence]:
    """
    Search GDELT DOC API and return Evidence objects.
    """

    url = settings.GDELT_BASE_URL

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": settings.SEARCH_RESULTS_PER_SOURCE,
    }

    response = requests.get(url, params=params)

    data = response.json()

    evidence = []

    for article in data.get("articles", []):

        evidence.append(
            Evidence(
                source="GDELT",
                url=article.get("url", ""),
                title=article.get("title", ""),
                raw_text=article.get("seendate", "") + "\n\n" +
                article.get("socialimage", ""),
                text=article.get("seendate", "") + "\n\n" +
                     article.get("socialimage", ""),
                cleaned="",
            )
        )

    return evidence

def _search_wikipedia(query: str) -> list[Evidence]:
    """
    Search Wikipedia using the MediaWiki Search API and
    return the top matching pages as Evidence objects.
    """

    search_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": settings.WIKIPEDIA_RESULTS,
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    evidence = []

    for result in data.get("query", {}).get("search", []):

        title = result.get("title")

        if not title:
            continue

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

    return evidence

def _search_wikidata(query: str) -> list[Evidence]:
    """
    Search Wikidata entities and return them as Evidence objects.
    """

    url = "https://www.wikidata.org/w/api.php"

    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query,
        "limit": 5,
    }

    response = requests.get(url, params=params)

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

def _search_tavily(query: str) -> list[Evidence]:
    """
    Search Tavily and convert the response into Evidence objects.
    """

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
                raw_text=result.get("content", "")
                or result.get("raw_content", ""),
                text=result.get("content", "")
                or result.get("raw_content", ""),
                cleaned="",
            )
        )

    return evidence



def search_claim(claim: ClaimNormalization) -> list[Evidence]:
    """
    Search all configured sources concurrently and return a unified list of
    Evidence objects.
    """

    with ThreadPoolExecutor(max_workers=settings.SEARCH_WORKERS) as executor:

        tavily_future = executor.submit(
            _search_tavily,
            claim.search_queries.tavily,
        )

        wikipedia_future = executor.submit(
            _search_wikipedia,
            claim.search_queries.wikipedia,
        )

        wikidata_future = executor.submit(
            _search_wikidata,
            claim.search_queries.wikidata,
        )

        gdelt_future = executor.submit(
            _search_gdelt,
            claim.search_queries.gdelt,
        )

        evidence = []

        evidence.extend(tavily_future.result())
        evidence.extend(wikipedia_future.result())
        evidence.extend(wikidata_future.result())
        evidence.extend(gdelt_future.result())

    return evidence
