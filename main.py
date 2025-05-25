import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from src.models.paper import Paper # Ensure this path is correct based on your structure
from src.services import arxiv_service # Ensure this path is correct

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ArXiv Paper Viewer API",
    description="API for browsing and searching arXiv papers.",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

logger.info("Application startup complete.")

@app.get("/", response_class=FileResponse)
async def root():
    return "frontend/static/index.html"

@app.get("/papers/latest", response_model=List[Paper], summary="Get Latest Papers", description="Fetches the most recently submitted papers from arXiv, with pagination.")
async def api_get_latest_papers(start: int = 0, max_results: int = 25):
    try:
        papers = await arxiv_service.get_latest_papers(start=start, max_results=max_results)
        return papers
    except Exception as e:
        logger.error(f"Error in /papers/latest endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching latest papers.")

@app.get("/papers/search", response_model=List[Paper], summary="Search Papers", description="Searches papers on arXiv by keyword, with pagination.")
async def api_search_papers(keyword: str, start: int = 0, max_results: int = 25):
    if not keyword or not keyword.strip(): # Added check for empty or whitespace-only keyword
        logger.warning(f"Search attempt with empty keyword: '{keyword}'")
        raise HTTPException(status_code=400, detail="Keyword cannot be empty or just whitespace.")
    try:
        papers = await arxiv_service.search_papers_by_keyword(keyword=keyword, start=start, max_results=max_results)
        return papers
    except Exception as e:
        logger.error(f"Error in /papers/search endpoint (keyword: {keyword}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while searching papers.")

# To run the app (for development):
# uvicorn main:app --reload