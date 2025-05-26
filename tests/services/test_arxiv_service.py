import pytest
import httpx
from respx import MockRouter
from typing import List

from src.models.paper import Paper, PaperAuthor
from src.services.arxiv_service import fetch_papers, get_latest_papers, search_papers_by_keyword, ARXIV_API_URL

# Sample Atom XML for mocking responses
SAMPLE_ATOM_XML_SUCCESS = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <updated>2023-01-01T10:00:00Z</updated>
    <published>2023-01-01T12:00:00Z</published>
    <title>Test Paper Title 1</title>
    <summary>This is a summary of the first test paper. </summary>
    <author><name>Author One</name></author>
    <author><name>Author Two</name></author>
    <link href="http://arxiv.org/abs/2301.00001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2301.00001v1" rel="related" type="application/pdf"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2301.00002v2</id>
    <published>2023-01-02T15:00:00Z</published>
    <title>Test Paper Title 2: Updated</title>
    <summary>This is a summary of the second test paper. No explicit updated tag, uses published. </summary>
    <author><name>Author Three</name></author>
    <link href="http://arxiv.org/abs/2301.00002v2" rel="alternate" type="text/html"/>
    <category term="math.CO" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2301.00003v1</id>
    <updated>2023-01-03T18:00:00Z</updated>
    <published>2023-01-03T18:00:00Z</published>
    <title>Test Paper Title 3: No PDF Link</title>
    <summary>This paper has no PDF link provided in any form. </summary>
    <author><name>Author Four</name></author>
    <link href="http://someotherdomain.com/paper/2301.00003v1" rel="alternate" type="text/html"/>
    <category term="physics.HE" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""

SAMPLE_ATOM_XML_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>
"""

MALFORMED_XML = "This is not XML, it's just a string."

@pytest.mark.asyncio
async def test_fetch_papers_success(respx_router: MockRouter):
    respx_router.get(ARXIV_API_URL).mock(return_value=httpx.Response(200, text=SAMPLE_ATOM_XML_SUCCESS))
    
    papers = await fetch_papers(search_query="cat:cs.AI")
    
    assert len(papers) == 3
    
    # Paper 1 assertions
    paper1 = papers[0]
    assert paper1.arxiv_id == "2301.00001v1"
    assert paper1.title == "Test Paper Title 1"
    assert paper1.summary.strip() == "This is a summary of the first test paper."
    assert len(paper1.authors) == 2
    assert paper1.authors[0].name == "Author One"
    assert paper1.authors[1].name == "Author Two"
    assert paper1.published_date == "2023-01-01T12:00:00Z"
    assert paper1.updated_date == "2023-01-01T10:00:00Z"
    assert str(paper1.pdf_url) == "http://arxiv.org/pdf/2301.00001v1"
    assert "cs.AI" in paper1.categories
    assert "cs.LG" in paper1.categories

    # Paper 2 assertions (no explicit updated, PDF link fallback from abs link)
    paper2 = papers[1]
    assert paper2.arxiv_id == "2301.00002v2"
    assert paper2.title == "Test Paper Title 2: Updated"
    assert paper2.published_date == "2023-01-02T15:00:00Z"
    assert paper2.updated_date == "2023-01-02T15:00:00Z" # Falls back to published_date
    assert str(paper2.pdf_url) == "http://arxiv.org/pdf/2301.00002v2" 
    assert "math.CO" in paper2.categories

    # Paper 3 assertions (no PDF link resolvable)
    paper3 = papers[2]
    assert paper3.arxiv_id == "2301.00003v1"
    assert paper3.title == "Test Paper Title 3: No PDF Link"
    assert paper3.pdf_url is None

@pytest.mark.asyncio
async def test_fetch_papers_empty_response(respx_router: MockRouter):
    respx_router.get(ARXIV_API_URL).mock(return_value=httpx.Response(200, text=SAMPLE_ATOM_XML_EMPTY))
    papers = await fetch_papers(search_query="cat:cs.AI")
    assert len(papers) == 0

@pytest.mark.asyncio
async def test_fetch_papers_http_error(respx_router: MockRouter, caplog):
    respx_router.get(ARXIV_API_URL).mock(return_value=httpx.Response(500, text="Internal Server Error"))
    papers = await fetch_papers(search_query="cat:cs.AI")
    assert len(papers) == 0
    assert "HTTP error occurred: 500 - Internal Server Error" in caplog.text
    assert "An unexpected error occurred in fetch_papers" not in caplog.text # Should be handled by specific except block

@pytest.mark.asyncio
async def test_fetch_papers_request_error(respx_router: MockRouter, caplog):
    respx_router.get(ARXIV_API_URL).mock(side_effect=httpx.RequestError("Connection failed"))
    papers = await fetch_papers(search_query="cat:cs.AI")
    assert len(papers) == 0
    assert "Request error occurred: Connection failed" in caplog.text
    assert "An unexpected error occurred in fetch_papers" not in caplog.text # Should be handled by specific except block

@pytest.mark.asyncio
async def test_fetch_papers_malformed_xml(respx_router: MockRouter, caplog):
    respx_router.get(ARXIV_API_URL).mock(return_value=httpx.Response(200, text=MALFORMED_XML))
    papers = await fetch_papers(search_query="cat:cs.AI")
    assert len(papers) == 0
    # This will be caught by the generic `except Exception` in fetch_papers
    assert "An unexpected error occurred in fetch_papers" in caplog.text
    # More specific error from feedparser might be "SAXParseException" or similar if it logs too
    # For now, checking our custom log is sufficient.

@pytest.mark.asyncio
async def test_get_latest_papers(respx_router: MockRouter):
    expected_query_params = {
        "search_query": "cat:cs.AI OR cat:math.CO OR cat:physics.hep-ph",
        "start": "0", # httpx stringifies params, so respx needs to match that
        "max_results": "2",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    # Ensure the URL matches exactly, including query params
    respx_router.get(ARXIV_API_URL, params=expected_query_params).mock(
        return_value=httpx.Response(200, text=SAMPLE_ATOM_XML_SUCCESS)
    )
    
    papers = await get_latest_papers(start=0, max_results=2)
    
    assert len(papers) == 3 # Our sample XML has 3 entries
    assert papers[0].title == "Test Paper Title 1"

@pytest.mark.asyncio
async def test_search_papers_by_keyword(respx_router: MockRouter):
    keyword = "quantum computing"
    expected_query_params = {
        "search_query": f"all:{keyword}",
        "start": "0",
        "max_results": "5", # Using a different max_results for this test
        "sortBy": "submittedDate", 
        "sortOrder": "descending",
    }
    respx_router.get(ARXIV_API_URL, params=expected_query_params).mock(
        return_value=httpx.Response(200, text=SAMPLE_ATOM_XML_SUCCESS)
    )
    
    papers = await search_papers_by_keyword(keyword=keyword, start=0, max_results=5)
    
    assert len(papers) == 3 # Sample XML has 3 entries
    assert papers[0].title == "Test Paper Title 1"
# Ensure pytest, pytest-asyncio, and respx are in requirements-dev.txt or requirements.txt
# `respx_router` is a fixture automatically provided by `respx`.
# `caplog` is a fixture automatically provided by `pytest` for log capturing.
# The `params` for `respx_router.get` should match how `httpx` sends them;
# typically, integer parameters are stringified in the query string.
# Example: `?start=0&max_results=10`.
# `respx` matches these stringified versions.
# Corrected log assertions for HTTP and Request errors to not expect the generic "unexpected error" log.
# For malformed XML, the generic exception handler in `fetch_papers` is expected to catch it.
# For `get_latest_papers` and `search_papers_by_keyword`, params in `respx_router.get` must match stringified values.
# For `test_search_papers_by_keyword` changed `max_results` to 5 to differentiate the mocked call if needed.
# The number of papers returned (3) is based on the SAMPLE_ATOM_XML_SUCCESS, not max_results.
# The `max_results` in the test function call and `expected_query_params` should align.
# For `test_get_latest_papers` max_results is 2. For `test_search_papers_by_keyword` max_results is 5.
# The actual number of papers returned by the service mock is driven by the content of `SAMPLE_ATOM_XML_SUCCESS` (which has 3 entries).
# The `max_results` parameter in the service call is what's sent to the (mocked) arXiv API.
# It's important that `respx` is configured to expect the correct `max_results` in the query params.
# The test for `get_latest_papers` uses `max_results=2`.
# The test for `search_papers_by_keyword` uses `max_results=5`.
# This is correctly reflected in `expected_query_params`.
# The number of papers asserted (`assert len(papers) == 3`) is correct because the mock returns all 3 entries from `SAMPLE_ATOM_XML_SUCCESS`.
# The `max_results` parameter is about the request to arXiv, not a post-filter on the results within `fetch_papers`.
# The test for PDF link fallback on paper2 was also confirmed to be correct: `http://arxiv.org/pdf/2301.00002v2`
# (derived from `<link href="http://arxiv.org/abs/2301.00002v2" />`).
# The test for paper3 (no PDF link) correctly asserts `paper3.pdf_url is None`.
# All looks consistent now.I have created the `tests/services/test_arxiv_service.py` file with the tests for the arXiv service. The tests cover successful fetching, various error conditions (HTTP errors, request errors, malformed XML), and the helper functions `get_latest_papers` and `search_papers_by_keyword`. `respx` is used for mocking HTTP calls, and `caplog` for asserting log messages.

Now I will proceed to **Step 3: Write Tests for `main.py` API Endpoints (`tests/test_main.py`)**.

I will create the `tests/test_main.py` file and implement tests for the `/`, `/papers/latest`, and `/papers/search` endpoints using `fastapi.testing.TestClient` and `unittest.mock.patch`.
