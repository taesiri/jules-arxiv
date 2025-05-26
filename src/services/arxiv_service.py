import httpx
import feedparser
import logging
from typing import List, Optional

from src.models.paper import Paper, PaperAuthor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query?"

async def fetch_papers(
    search_query: str,
    start: int = 0,
    max_results: int = 10,
    sortBy: str = "submittedDate",
    sortOrder: str = "descending"
) -> List[Paper]:
    """
    Fetches papers from the arXiv API based on a search query and other parameters.
    """
    query_params = {
        "search_query": search_query,
        "start": start,
        "max_results": max_results,
        "sortBy": sortBy,
        "sortOrder": sortOrder,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Construct the full URL for logging
            import urllib.parse
            full_url = f"{ARXIV_API_URL}{urllib.parse.urlencode(query_params)}"
            logger.info(f"Fetching papers from arXiv. URL: {full_url}")
            # The previous log for params is still useful for a structured view
            logger.info(f"Query parameters: {query_params}")
            response = await client.get(ARXIV_API_URL, params=query_params)
            response.raise_for_status()  # Raise an exception for bad status codes

        feed = feedparser.parse(response.text)
        
        papers = []
        for entry in feed.entries:
            # Extract arXiv ID
            arxiv_id_raw = entry.get("id", "")
            arxiv_id = arxiv_id_raw.split('/abs/')[-1] if '/abs/' in arxiv_id_raw else arxiv_id_raw

            # Find PDF link
            pdf_url = None
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href")
                    break
            if not pdf_url and entry.get("link"):  # Fallback if PDF link type is not explicit
                if "/abs/" in entry.link:
                    pdf_url = entry.link.replace('/abs/', '/pdf/')

            paper_authors = [PaperAuthor(name=author.get("name", "N/A")) for author in entry.get("authors", [])]
            
            paper_data = Paper(
                arxiv_id=arxiv_id,
                title=entry.get("title", "N/A"),
                summary=entry.get("summary", "N/A").strip(),
                authors=paper_authors,
                published_date=entry.get("published", "N/A"),
                updated_date=entry.get("updated", entry.get("published", "N/A")), # Fallback to published_date if updated is missing
                pdf_url=pdf_url,
                categories=[tag.get('term', 'N/A') for tag in entry.get('tags', [])]
            )
            papers.append(paper_data)
        
        logger.info(f"Successfully fetched {len(papers)} papers.")
        return papers

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}", exc_info=True)
        return []
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred in fetch_papers: {e}", exc_info=True)
        return []

async def get_latest_papers(start: int = 0, max_results: int = 25) -> List[Paper]:
    """
    Fetches the latest papers from arXiv from pre-defined categories.
    """
    # General query for recent papers in AI, Math (Combinatorics), and Physics (High Energy Physics)
    search_query = "cat:cs.AI OR cat:math.CO OR cat:physics.hep-ph"
    logger.info(f"Fetching latest papers with query: '{search_query}', start: {start}, max_results: {max_results}")
    return await fetch_papers(
        search_query=search_query,
        start=start,
        max_results=max_results,
        sortBy="submittedDate",
        sortOrder="descending"
    )

async def search_papers_by_keyword(keyword: str, start: int = 0, max_results: int = 25) -> List[Paper]:
    """
    Searches papers on arXiv by a specific keyword.
    The search query targets all fields for the given keyword.
    """
    search_query = f"all:{keyword}"
    logger.info(f"Searching papers by keyword: '{keyword}', start: {start}, max_results: {max_results}")
    return await fetch_papers(
        search_query=search_query,
        start=start,
        max_results=max_results,
        # Using relevance for keyword search might be better, but sticking to submittedDate for now
        # sortBy="relevance", 
        sortBy="submittedDate",
        sortOrder="descending"
    )

if __name__ == '__main__':
    import asyncio

    async def main_test():
        print("Testing get_latest_papers...")
        latest_papers = await get_latest_papers(max_results=2)
        if latest_papers:
            for paper in latest_papers:
                print(f"  Title: {paper.title}")
                print(f"  ID: {paper.arxiv_id}")
                print(f"  Authors: {', '.join([author.name for author in paper.authors])}")
                print(f"  Published: {paper.published_date}")
                print(f"  PDF URL: {paper.pdf_url}")
                print(f"  Categories: {paper.categories}")
                print(f"  Summary: {paper.summary[:100]}...")
                print("-" * 20)
        else:
            print("  No latest papers found or an error occurred.")

        print("\nTesting search_papers_by_keyword (keyword: 'quantum computing')...")
        searched_papers = await search_papers_by_keyword(keyword="quantum computing", max_results=2)
        if searched_papers:
            for paper in searched_papers:
                print(f"  Title: {paper.title}")
                print(f"  ID: {paper.arxiv_id}")
                print(f"  Authors: {', '.join([author.name for author in paper.authors])}")
                print(f"  Published: {paper.published_date}")
                print(f"  PDF URL: {paper.pdf_url}")
                print(f"  Categories: {paper.categories}")
                print(f"  Summary: {paper.summary[:100]}...")
                print("-" * 20)
        else:
            print("  No papers found for 'quantum computing' or an error occurred.")

    asyncio.run(main_test())
