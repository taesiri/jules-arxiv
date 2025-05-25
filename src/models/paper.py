from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class PaperAuthor(BaseModel):
    name: str

class Paper(BaseModel):
    arxiv_id: str
    title: str
    summary: str
    authors: List[PaperAuthor]
    published_date: str 
    updated_date: Optional[str] = None
    pdf_url: Optional[HttpUrl] = None
    categories: Optional[List[str]] = None
