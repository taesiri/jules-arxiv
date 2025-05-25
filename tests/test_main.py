import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock # AsyncMock for async functions

from main import app # Assuming your FastAPI app instance is named 'app' in main.py
from src.models.paper import Paper, PaperAuthor # For creating mock return values

client = TestClient(app)

# Sample Paper data for mocking service responses
mock_paper_1 = Paper(
    arxiv_id="2301.00001v1",
    title="Mock Paper 1",
    summary="Summary for mock paper 1.",
    authors=[PaperAuthor(name="Author A"), PaperAuthor(name="Author B")],
    published_date="2023-01-01T10:00:00Z",
    updated_date="2023-01-01T12:00:00Z",
    pdf_url="http://arxiv.org/pdf/2301.00001v1",
    categories=["cs.AI"]
)
mock_paper_2 = Paper(
    arxiv_id="2301.00002v1",
    title="Mock Paper 2",
    summary="Summary for mock paper 2.",
    authors=[PaperAuthor(name="Author C")],
    published_date="2023-01-02T14:00:00Z",
    updated_date="2023-01-02T14:00:00Z",
    pdf_url="http://arxiv.org/pdf/2301.00002v1",
    categories=["math.CO"]
)
mock_papers_list = [mock_paper_1, mock_paper_2]

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ArXiv Paper Viewer API"}

@patch("src.services.arxiv_service.get_latest_papers", new_callable=AsyncMock)
def test_get_latest_papers_success(mock_get_latest):
    mock_get_latest.return_value = mock_papers_list
    
    response = client.get("/papers/latest?start=0&max_results=2")
    
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response[0]["title"] == "Mock Paper 1"
    assert json_response[1]["arxiv_id"] == "2301.00002v1"
    
    mock_get_latest.assert_called_once_with(start=0, max_results=2)

@patch("src.services.arxiv_service.get_latest_papers", new_callable=AsyncMock)
def test_get_latest_papers_service_exception(mock_get_latest):
    mock_get_latest.side_effect = Exception("Service layer exploded")
    
    response = client.get("/papers/latest")
    
    assert response.status_code == 500
    json_response = response.json()
    # The detail message comes from main.py's error handler for /papers/latest
    assert "An unexpected error occurred while fetching latest papers." in json_response["detail"]
    # Check if the logger in main.py's endpoint was called (optional, requires more setup or checking caplog)

@patch("src.services.arxiv_service.search_papers_by_keyword", new_callable=AsyncMock)
def test_search_papers_success(mock_search_keyword):
    mock_search_keyword.return_value = [mock_paper_1] # Return only one paper for this test
    
    response = client.get("/papers/search?keyword=test&start=0&max_results=1")
    
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["title"] == "Mock Paper 1"
    
    mock_search_keyword.assert_called_once_with(keyword="test", start=0, max_results=1)

@patch("src.services.arxiv_service.search_papers_by_keyword", new_callable=AsyncMock)
def test_search_papers_empty_keyword(mock_search_keyword):
    # No need to mock return_value as it shouldn't be called
    response = client.get("/papers/search?keyword=")
    assert response.status_code == 400
    assert response.json()["detail"] == "Keyword cannot be empty or just whitespace."
    mock_search_keyword.assert_not_called()

    response_whitespace = client.get("/papers/search?keyword=   ")
    assert response_whitespace.status_code == 400
    assert response_whitespace.json()["detail"] == "Keyword cannot be empty or just whitespace."
    mock_search_keyword.assert_not_called()
    
    # Test with no keyword param
    response_no_keyword = client.get("/papers/search")
    assert response_no_keyword.status_code == 422 # FastAPI's handling of missing required query parameter

@patch("src.services.arxiv_service.search_papers_by_keyword", new_callable=AsyncMock)
def test_search_papers_service_exception(mock_search_keyword):
    mock_search_keyword.side_effect = Exception("Search service went boom")
    
    response = client.get("/papers/search?keyword=validkeyword")
    
    assert response.status_code == 500
    json_response = response.json()
    # The detail message comes from main.py's error handler for /papers/search
    assert "An unexpected error occurred while searching papers." in json_response["detail"]

# To run these tests:
# Ensure FastAPI app is 'app' in 'main.py'
# Ensure 'pytest', 'fastapi[all]' (for TestClient), 'uvicorn', 'python-multipart' (often needed),
# and 'unittest.mock' (standard library but good to be aware) are available.
# `new_callable=AsyncMock` is crucial for patching async functions.
# The detail in error messages for 500 errors in these tests matches what's in main.py's exception handlers.
# The test for empty keyword in search also checks for whitespace-only and missing keyword.
# FastAPI returns 422 for missing required query parameters.
# The JSON response for Paper models should match Pydantic's serialization (e.g. HttpUrl to str).
# `mock_paper_1.pdf_url` is an `HttpUrl` object, but when FastAPI serializes it, it becomes a string.
# The tests implicitly check this by comparing the structure. For more explicit checks on specific fields like pdf_url,
# you'd access `json_response[0]["pdf_url"]` and assert its string value.
# The current assertions are on title and arxiv_id which are strings.
# If `pdf_url` were `None`, it would be `null` in JSON, or omitted if `exclude_none=True` in Pydantic model config (not default).
# Our Paper model has `Optional[HttpUrl]`, so if `pdf_url` is None, it serializes to `null`.
# `mock_paper_1` and `mock_paper_2` have valid pdf_url strings, which Pydantic converts to HttpUrl.
# These are then serialized back to strings by FastAPI in the JSON response.
# So, `json_response[0]["pdf_url"]` would be "http://arxiv.org/pdf/2301.00001v1".
# Adding an explicit check for this:
@patch("src.services.arxiv_service.get_latest_papers", new_callable=AsyncMock)
def test_get_latest_papers_pdf_url_serialization(mock_get_latest):
    mock_get_latest.return_value = [mock_paper_1]
    response = client.get("/papers/latest?start=0&max_results=1")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["pdf_url"] == str(mock_paper_1.pdf_url) # Explicitly check string form

# Test for paper with None pdf_url
mock_paper_no_pdf = Paper(
    arxiv_id="2301.00003v1",
    title="Mock Paper No PDF",
    summary="Summary for mock paper with no PDF.",
    authors=[PaperAuthor(name="Author D")],
    published_date="2023-01-03T10:00:00Z",
    updated_date="2023-01-03T12:00:00Z",
    pdf_url=None, # Explicitly None
    categories=["cs.CV"]
)

@patch("src.services.arxiv_service.get_latest_papers", new_callable=AsyncMock)
def test_get_latest_papers_none_pdf_url_serialization(mock_get_latest):
    mock_get_latest.return_value = [mock_paper_no_pdf]
    response = client.get("/papers/latest?start=0&max_results=1")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["pdf_url"] is None # Pydantic serializes None to null in JSON
    assert json_response[0]["title"] == "Mock Paper No PDF"I have created `tests/test_main.py` with unit tests for the API endpoints.
These tests cover:
-   The root `/` endpoint.
-   `/papers/latest` endpoint:
    -   Successful response with mocked service data.
    -   Correct passing of `start` and `max_results` parameters to the service.
    -   Handling of service layer exceptions, returning a 500 error.
    -   Correct serialization of `pdf_url` (including `None` values).
-   `/papers/search` endpoint:
    -   Successful response with mocked service data for a given keyword.
    -   Correct passing of `keyword`, `start`, and `max_results` to the service.
    -   Handling of empty or whitespace-only keywords (400 error).
    -   Handling of missing keyword parameter (422 error by FastAPI).
    -   Handling of service layer exceptions, returning a 500 error.

`TestClient` is used to make requests to the app, and `unittest.mock.patch` with `AsyncMock` is used to mock the asynchronous service functions (`get_latest_papers` and `search_papers_by_keyword`). Sample `Paper` objects are defined to be used as return values for these mocks.

The testing setup seems complete according to the subtask requirements.

I have completed:
1.  **Set up Testing Environment**:
    *   `pytest`, `pytest-asyncio`, `respx` were added to `requirements.txt` (in the previous subtask turn, but intended for this one).
    *   `tests` directory with `__init__.py` and `tests/services/__init__.py` were created (similarly, in previous subtask turn).
2.  **Write Tests for `arxiv_service.py`**:
    *   Created `tests/services/test_arxiv_service.py` with comprehensive tests for `fetch_papers`, `get_latest_papers`, and `search_papers_by_keyword` using `respx` and `caplog`.
3.  **Write Tests for `main.py` API Endpoints**:
    *   Created `tests/test_main.py` with tests for all API endpoints (`/`, `/papers/latest`, `/papers/search`) using `TestClient` and `unittest.mock.patch` with `AsyncMock`.

All parts of the subtask have been addressed.
